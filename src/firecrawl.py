import json
import os
import asyncio
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class FirecrawlMCPService:
    """Calls the Firecrawl MCP server over stdio as a drop-in for the old FirecrawlService.

    Each public method spins up a fresh MCP session, calls one tool, and returns
    the parsed result in the same shape the rest of the codebase already expects.
    """

    def __init__(self) -> None:
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise RuntimeError("FIRECRAWL_API_KEY is required to initialize FirecrawlMCPService.")
        # Merge the full parent environment so npx can resolve node on PATH.
        self._server_params = StdioServerParameters(
            command="npx",
            args=["-y", "firecrawl-mcp"],
            env={**os.environ, "FIRECRAWL_API_KEY": api_key},
        )

    async def _call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Open a fresh MCP session, invoke one tool, and return the parsed JSON payload."""
        async with stdio_client(self._server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
        # Firecrawl MCP tools always return a single TextContent block containing JSON.
        if result.content and hasattr(result.content[0], "text"):
            return json.loads(result.content[0].text)
        return None

    def search(self, query: str, num_results: int = 5) -> Any:
        try:
            response = asyncio.run(
                self._call_tool(
                    "firecrawl_search",
                    {
                        "query": query,
                        "limit": num_results,
                        "scrapeOptions": {"formats": ["markdown"]},
                    },
                )
            )
            # Return just the data list — _normalize_search_results in workflow.py
            # falls back to iterating the value directly when there is no .data attribute.
            if isinstance(response, dict):
                return response.get("data", [])
            return response or []
        except Exception as exc:
            print(f"Error during search: {exc}")
            return []

    def scrape_url(self, url: str) -> Any:
        try:
            # Return the full dict: _extract_markdown expects {"markdown": "..."}.
            return asyncio.run(
                self._call_tool("firecrawl_scrape", {"url": url, "formats": ["markdown"]})
            )
        except Exception as exc:
            print(f"Error during scrape: {exc}")
            return None
