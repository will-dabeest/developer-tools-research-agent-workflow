from pydantic import BaseModel


class CompanyAnalysis(BaseModel):
    """Structured LLM output for a single developer tool."""

    pricing_model: str  # "Free" | "Freemium" | "Paid" | "Enterprise" | "Unknown"
    description: str = ""
    is_open_source: bool | None = None
    api_available: bool | None = None
    tech_stack: list[str] = []
    language_support: list[str] = []
    integration_capabilities: list[str] = []


class CompanyInfo(BaseModel):
    """All known information about a developer tool or company."""

    name: str
    description: str
    website: str
    pricing_model: str | None = None
    is_open_source: bool | None = None
    api_available: bool | None = None
    developer_experience_rating: str | None = None  # "Poor" | "Good" | "Excellent"
    tech_stack: list[str] = []
    competitors: list[str] = []
    language_support: list[str] = []
    integration_capabilities: list[str] = []


class ResearchState(BaseModel):
    """Shared state passed between LangGraph workflow nodes."""

    query: str  # Store the initial user request that drives the graph.
    extracted_tools: list[str] = []  # Store candidate tool names found during extraction.
    companies: list[CompanyInfo] = []  # Store final researched tools/companies.
    analysis: str | None = None  # Store the final recommendation summary.