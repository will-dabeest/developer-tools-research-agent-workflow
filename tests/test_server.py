from unittest.mock import MagicMock, patch

from server import _format_results, research_dev_tools
from src.models import CompanyInfo, ResearchState


def _make_company(**kwargs) -> CompanyInfo:
    defaults = dict(
        name="Pinecone",
        website="https://pinecone.io",
        description="Vector database",
        pricing_model="Freemium",
        is_open_source=False,
        api_available=True,
        tech_stack=["Python"],
        language_support=["Python", "Go"],
        integration_capabilities=["AWS"],
    )
    return CompanyInfo(**{**defaults, **kwargs})


def test_format_results_renders_companies_and_analysis():
    state = ResearchState(
        query="vector databases",
        companies=[_make_company()],
        analysis="Use Pinecone for production.",
    )
    result = _format_results(state)
    assert "vector databases" in result
    assert "Pinecone" in result
    assert "https://pinecone.io" in result
    assert "Freemium" in result
    assert "Use Pinecone for production." in result


def test_format_results_handles_empty_companies():
    state = ResearchState(query="vector databases")
    result = _format_results(state)
    assert "vector databases" in result
    assert isinstance(result, str)


def test_research_dev_tools_calls_workflow_and_returns_string():
    fake_state = ResearchState(
        query="vector databases",
        companies=[_make_company()],
        analysis="Use Pinecone.",
    )
    mock_workflow = MagicMock()
    mock_workflow.run.return_value = fake_state

    with patch("server.Workflow", return_value=mock_workflow):
        result = research_dev_tools("vector databases")

    mock_workflow.run.assert_called_once_with("vector databases")
    assert isinstance(result, str)
    assert len(result) > 0
