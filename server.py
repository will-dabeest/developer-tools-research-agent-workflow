import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from src.models import ResearchState
from src.workflow import Workflow

load_dotenv()

mcp = FastMCP(
    "dev-tools-researcher",
    instructions=(
        "Use research_dev_tools to look up and compare developer tools in a given category. "
        "The tool runs a multi-step web research workflow and returns structured results with "
        "pricing, open-source status, API availability, and a final recommendation."
    ),
)


def _format_results(state: ResearchState) -> str:
    """Render ResearchState as a readable text report (mirrors main.py output)."""
    lines: list[str] = [f"Research Results: {state.query}", "=" * 40]
    for i, company in enumerate(state.companies, start=1):
        lines += [
            f"\n{i}. {company.name}",
            f"   Website:      {company.website}",
            f"   Description:  {company.description}",
            f"   Pricing:      {company.pricing_model or 'Unknown'}",
            f"   Open Source:  {'Yes' if company.is_open_source else 'No'}",
            f"   API:          {'Yes' if company.api_available else 'No'}",
            f"   Tech Stack:   {', '.join(company.tech_stack) or 'N/A'}",
            f"   Languages:    {', '.join(company.language_support) or 'N/A'}",
            f"   Integrations: {', '.join(company.integration_capabilities) or 'N/A'}",
            "-" * 40,
        ]
    if state.analysis:
        lines += ["\nRecommendations:", "-" * 40, state.analysis]
    return "\n".join(lines)


@mcp.tool()
def research_dev_tools(query: str) -> str:
    """Research and compare developer tools in a given category.

    Runs a multi-step workflow that:
    1. Searches the web for tools matching the category
    2. Scrapes each tool's official site for structured details
    3. Returns pricing, open-source status, API availability, and recommendations

    Args:
        query: Category or type of developer tool to research.
               Examples: "vector databases", "CI/CD tools", "API gateways"

    Returns:
        A structured text report comparing the top tools found, with a final recommendation.
    """
    # Guard against any library writing to stdout, which would corrupt the stdio MCP stream.
    sys.stdout = sys.stderr
    try:
        workflow = Workflow()
        state = workflow.run(query)
        return _format_results(state)
    finally:
        sys.stdout = sys.__stdout__


def main() -> None:
    # Run with stdio transport — the default for MCP server subprocesses.
    mcp.run()


if __name__ == "__main__":
    main()
