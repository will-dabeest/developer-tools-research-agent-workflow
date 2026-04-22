import os
from collections.abc import Mapping
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from .firecrawl import FirecrawlMCPService
from .models import CompanyAnalysis, CompanyInfo, ResearchState
from .prompts import DeveloperToolsPrompts

# Define runtime/config constants used across workflow steps.
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# Cap per-page content to keep latency and model context usage predictable.
MAX_CONTENT_CHARS = 2_500
# Cap article snippets during extraction to reduce noise and prompt size.
MAX_ARTICLE_CHARS = 1_500
MAX_TOOLS = 4


def _normalize_search_results(search_results: Any) -> list[dict[str, Any]]:
    """Convert any Firecrawl search response into a plain list of dicts."""
    raw_items = getattr(search_results, "data", search_results)
    if not raw_items:
        return []
    normalized: list[dict[str, Any]] = []
    for item in raw_items:
        if isinstance(item, Mapping):
            normalized.append(dict(item))
        elif hasattr(item, "model_dump"):
            normalized.append(item.model_dump())
    return normalized


def _extract_markdown(document: Any) -> str:
    """Safely extract markdown text from a Firecrawl scrape result."""
    if not document:
        return ""
    if isinstance(document, Mapping):
        return str(document.get("markdown", ""))
    return str(getattr(document, "markdown", ""))


def _apply_analysis(company: CompanyInfo, analysis: CompanyAnalysis) -> None:
    """Update a CompanyInfo in-place with structured LLM analysis results."""
    company.pricing_model = analysis.pricing_model
    company.is_open_source = analysis.is_open_source
    company.tech_stack = analysis.tech_stack
    company.description = analysis.description
    company.api_available = analysis.api_available
    company.language_support = analysis.language_support
    company.integration_capabilities = analysis.integration_capabilities


class Workflow:
    def __init__(self) -> None:
        # Initialize external services and compile the graph once.
        self.firecrawl = FirecrawlMCPService()
        self.llm = ChatOllama(
            model=_OLLAMA_MODEL,
            temperature=0.1,
            base_url=_OLLAMA_BASE_URL,
        )
        self.prompts = DeveloperToolsPrompts()
        self.graph = self._build_graph()

    def _build_graph(self) -> Any:
        # Build graph flow: extract candidate tools -> research each tool -> synthesize recommendation.
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()

    def _extract_tools_step(self, state: ResearchState) -> dict[str, Any]:
        # Gather source content, then ask the LLM to extract tool names.
        print(f"Finding articles about: {state.query}")
        article_query = f"{state.query} tools comparison best alternatives"
        results = _normalize_search_results(self.firecrawl.search(article_query, num_results=3))

        all_content = ""
        for result in results:
            url = result.get("url", "")
            if not url:
                continue
            all_content += _extract_markdown(self.firecrawl.scrape_url(url))[:MAX_ARTICLE_CHARS] + "\n\n"

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content)),
        ]

        try:
            response = self.llm.invoke(messages)
            tool_names = [line.strip() for line in str(response.content).strip().split("\n") if line.strip()]
            print(f"Extracted tools: {', '.join(tool_names[:5])}")
            return {"extracted_tools": tool_names}
        except Exception as exc:
            print(f"Error during tool extraction: {exc}")
            return {"extracted_tools": []}
        
    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        # Use structured output so downstream code can rely on typed fields.
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)
        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content)),
        ]
        try:
            result = structured_llm.invoke(messages)
            if isinstance(result, CompanyAnalysis):
                return result
            elif isinstance(result, dict):
                return CompanyAnalysis(**result)
            elif hasattr(result, 'model_dump'):
                return CompanyAnalysis(**result.model_dump())
            else:
                raise ValueError("Unexpected result type from LLM")
        except Exception as exc:
            print(f"Error analyzing {company_name}: {exc}")
            return CompanyAnalysis(pricing_model="Unknown", description="Failed to analyze.")
        
    def _research_step(self, state: ResearchState) -> dict[str, Any]:
        # Prefer extracted tools, but fall back to direct search when extraction is empty.
        tool_names = state.extracted_tools[:MAX_TOOLS]

        if not tool_names:
            # Fall back so the workflow still returns useful output when extraction underperforms.
            print("No tools extracted, falling back to direct search.")
            items = _normalize_search_results(self.firecrawl.search(state.query, num_results=MAX_TOOLS))
            tool_names = [
                item.get("metadata", {}).get("title") or item.get("title") or "Unknown"
                for item in items
            ]

        print(f"Researching tools: {', '.join(tool_names)}")

        companies: list[CompanyInfo] = []
        for tool_name in tool_names:
            # Resolve one high-confidence URL per tool, then scrape and analyze it.
            items = _normalize_search_results(
                self.firecrawl.search(f"{tool_name} official site", num_results=1)
            )
            if not items:
                continue

            item = items[0]
            url = item.get("url", "")
            company = CompanyInfo(
                name=tool_name,
                description=(item.get("markdown", "") or "")[:MAX_CONTENT_CHARS],
                website=url,
            )

            if url:
                content = _extract_markdown(self.firecrawl.scrape_url(url))[:MAX_CONTENT_CHARS]
                if content:
                    _apply_analysis(company, self._analyze_company_content(tool_name, content))

            companies.append(company)

        return {"companies": companies}
    
    def _analyze_step(self, state: ResearchState) -> dict[str, Any]:
        # Generate a concise final recommendation over all researched companies.
        print("Generating final recommendations...")
        company_data = ", ".join(c.model_dump_json() for c in state.companies)
        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data)),
        ]
        response = self.llm.invoke(messages)
        return {"analysis": response.content}

    def run(self, query: str) -> ResearchState:
        # Run the graph for one query and return fully materialized state.
        final_state = self.graph.invoke(ResearchState(query=query))
        return ResearchState(**final_state)