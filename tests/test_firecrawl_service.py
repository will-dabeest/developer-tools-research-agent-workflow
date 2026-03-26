import pytest

from src.firecrawl import FirecrawlService


class RaiseOnSearchApp:
    def search(self, *args, **kwargs):
        raise RuntimeError("boom")


class RaiseOnScrapeApp:
    def scrape(self, *args, **kwargs):
        raise RuntimeError("boom")


def test_init_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="FIRECRAWL_API_KEY"):
        FirecrawlService()


def test_search_returns_empty_list_on_failure():
    service = object.__new__(FirecrawlService)
    service.app = RaiseOnSearchApp()
    assert service.search("vector db") == []


def test_scrape_url_returns_none_on_failure():
    service = object.__new__(FirecrawlService)
    service.app = RaiseOnScrapeApp()
    assert service.scrape_url("https://example.com") is None
