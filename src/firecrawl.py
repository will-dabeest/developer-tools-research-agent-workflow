import os
from typing import Any

from firecrawl import FirecrawlApp


class FirecrawlService:
    def __init__(self) -> None:
        # Fail fast if the Firecrawl API key is missing.
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise RuntimeError("FIRECRAWL_API_KEY is required to initialize FirecrawlService.")
        self.app = FirecrawlApp(api_key=api_key)

    def search(self, query: str, num_results: int = 5) -> Any:
        try:
            # Request markdown so downstream parsing can stay text-based.
            return self.app.search(
                query=query,
                limit=num_results,
                scrape_options={"formats": ["markdown"]},
            )
        except Exception as exc:
            print(f"Error during search: {exc}")
            # Return an empty list so callers can continue with fallback logic.
            return []

    def scrape_url(self, url: str) -> Any:
        try:
            # Scrape a single URL and normalize output to markdown.
            return self.app.scrape(url, formats=["markdown"])
        except Exception as exc:
            print(f"Error during scrape: {exc}")
            # Return None so callers can skip analysis for this URL and continue.
            return None