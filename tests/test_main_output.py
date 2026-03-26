from src.models import CompanyInfo
from main import print_company


def test_print_company_renders_expected_fields(capsys):
    company = CompanyInfo(
        name="ToolX",
        description="Test description",
        website="https://toolx.dev",
        pricing_model="Free",
        is_open_source=True,
        api_available=True,
        tech_stack=["Python", "Rust"],
        language_support=["Python"],
        integration_capabilities=["GitHub"],
    )

    print_company(1, company)
    out = capsys.readouterr().out

    expected_lines = [
        "1. ToolX",
        "Pricing Model:            Free",
        "Open Source:              Yes",
        "API Available:            Yes",
        "Tech Stack:               Python, Rust",
    ]

    for line in expected_lines:
        assert line in out
