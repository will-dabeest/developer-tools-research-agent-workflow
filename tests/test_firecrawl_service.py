import pytest
from unittest.mock import AsyncMock, patch

from src.firecrawl import FirecrawlMCPService


def test_init_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="FIRECRAWL_API_KEY"):
        FirecrawlMCPService()


def test_search_returns_empty_list_on_failure(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    service = FirecrawlMCPService()
    with patch.object(service, "_call_tool", new=AsyncMock(side_effect=RuntimeError("boom"))):
        assert service.search("vector db") == []


def test_scrape_url_returns_none_on_failure(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    service = FirecrawlMCPService()
    with patch.object(service, "_call_tool", new=AsyncMock(side_effect=RuntimeError("boom"))):
        assert service.scrape_url("https://example.com") is None
