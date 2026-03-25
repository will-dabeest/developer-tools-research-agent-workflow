from dotenv import load_dotenv

from src.models import CompanyInfo
from src.workflow import Workflow

load_dotenv()

# Define shared display separators for CLI output.
DIVIDER = "-" * 40
HEADER = "=" * 40


def print_company(i: int, company: CompanyInfo) -> None:
    # Render a single company/tool result in a consistent, scannable format.
    print(f"\n{i}. {company.name}")
    print(f"   Description:              {company.description}")
    print(f"   Website:                  {company.website}")
    print(f"   Pricing Model:            {company.pricing_model or 'Unknown'}")
    print(f"   Open Source:              {'Yes' if company.is_open_source else 'No'}")
    print(f"   API Available:            {'Yes' if company.api_available else 'No'}")
    print(f"   Tech Stack:               {', '.join(company.tech_stack) or 'N/A'}")
    print(f"   Language Support:         {', '.join(company.language_support) or 'N/A'}")
    print(f"   Integration Capabilities: {', '.join(company.integration_capabilities) or 'N/A'}")
    print(DIVIDER)


def main() -> None:
    # Build the workflow once and reuse it for the full REPL session.
    workflow = Workflow()
    print("Developer Tools Research Agent is running...")

    while True:
        try:
            # Read one query per loop iteration.
            query = input("\nEnter a developer tool category to research (or 'exit' to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if query.lower() in {"exit", "quit"}:
            print("Exiting...")
            break

        if not query:
            continue

        # Run the end-to-end research workflow for the entered query.
        result = workflow.run(query)
        print(f"\nResearch Results: {query}")
        print(HEADER)

        for i, company in enumerate(result.companies, start=1):
            print_company(i, company)

        if result.analysis:
            print("\nDeveloper Recommendations:")
            print(DIVIDER)
            print(result.analysis)


if __name__ == "__main__":
    main()

