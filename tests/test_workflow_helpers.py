from src.models import CompanyAnalysis, CompanyInfo
from src.workflow import _apply_analysis, _extract_markdown, _normalize_search_results


class Dumpable:
    def model_dump(self):
        return {"title": "Tool A", "url": "https://example.com"}


class SearchWrapper:
    def __init__(self, data):
        self.data = data


class Doc:
    markdown = "# hello"


def test_normalize_search_results_supports_data_attr_and_model_dump():
    wrapped = SearchWrapper([Dumpable()])
    result = _normalize_search_results(wrapped)
    assert result == [{"title": "Tool A", "url": "https://example.com"}]


def test_extract_markdown_supports_mapping_and_attr():
    assert _extract_markdown({"markdown": "map md"}) == "map md"
    assert _extract_markdown(Doc()) == "# hello"
    assert _extract_markdown(None) == ""


def test_apply_analysis_updates_company_fields():
    company = CompanyInfo(name="X", description="", website="https://x.com")
    analysis = CompanyAnalysis(
        pricing_model="Freemium",
        description="Developer platform",
        is_open_source=True,
        api_available=True,
        tech_stack=["Python"],
        language_support=["Python", "TypeScript"],
        integration_capabilities=["GitHub"],
    )

    _apply_analysis(company, analysis)

    assert company.pricing_model == "Freemium"
    assert company.description == "Developer platform"
    assert company.is_open_source is True
    assert company.api_available is True
    assert company.tech_stack == ["Python"]
    assert company.language_support == ["Python", "TypeScript"]
    assert company.integration_capabilities == ["GitHub"]
