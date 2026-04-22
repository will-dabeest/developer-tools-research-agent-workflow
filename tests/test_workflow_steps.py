from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.models import CompanyInfo, ResearchState
from src.workflow import Workflow


def _make_workflow() -> Workflow:
    with (
        patch("src.workflow.FirecrawlMCPService"),
        patch("src.workflow.ChatOllama"),
    ):
        return Workflow()


def _fake_search_result(url: str = "https://example.com") -> list[dict]:
    return [{"url": url, "markdown": "Some content about the tool."}]


def _fake_scrape_result(text: str = "Tool homepage content."):
    return SimpleNamespace(markdown=text)


def test_extract_tools_step_returns_tool_names():

    workflow = _make_workflow()
    workflow.firecrawl.search = MagicMock(return_value=_fake_search_result())
    workflow.firecrawl.scrape_url = MagicMock(return_value=_fake_scrape_result())
    workflow.llm.invoke = MagicMock(return_value=SimpleNamespace(content="Pinecone\nWeaviate\nChroma"))

    result = workflow._extract_tools_step(ResearchState(query="vector databases"))

    assert result["extracted_tools"] == ["Pinecone", "Weaviate", "Chroma"]


def test_extract_tools_step_returns_empty_on_llm_failure():

    workflow = _make_workflow()
    workflow.firecrawl.search = MagicMock(return_value=_fake_search_result())
    workflow.firecrawl.scrape_url = MagicMock(return_value=_fake_scrape_result())
    workflow.llm.invoke = MagicMock(side_effect=RuntimeError("LLM unavailable"))

    result = workflow._extract_tools_step(ResearchState(query="vector databases"))

    assert result["extracted_tools"] == []


def test_analyze_step_returns_analysis_string():

    workflow = _make_workflow()
    workflow.llm.invoke = MagicMock(return_value=SimpleNamespace(content="Use Pinecone for production."))

    state = ResearchState(
        query="vector databases",
        companies=[
            CompanyInfo(name="Pinecone", description="Vector DB", website="https://pinecone.io")
        ],
    )
    result = workflow._analyze_step(state)

    assert result["analysis"] == "Use Pinecone for production."
