"""Firecrawl service for official company and recent-news research."""

from __future__ import annotations

import os
from typing import Any

from firecrawl import Firecrawl


class FirecrawlService:
    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not key:
            raise ValueError("FIRECRAWL_API_KEY is missing")
        self.client = Firecrawl(api_key=key)

    @staticmethod
    def _get(value: Any, field: str, default: Any = None) -> Any:
        return value.get(field, default) if isinstance(value, dict) else getattr(value, field, default)

    def _normalize(self, item: Any, source_type: str) -> dict[str, Any]:
        metadata = self._get(item, "metadata", {}) or {}
        return {
            "title": self._get(item, "title") or self._get(metadata, "title"),
            "url": self._get(item, "url") or self._get(metadata, "source_url") or self._get(metadata, "sourceURL"),
            "content": self._get(item, "markdown") or self._get(item, "content") or self._get(item, "description") or "",
            "published_date": self._get(item, "published_date") or self._get(metadata, "published_date"),
            "source_type": source_type,
            "source_provider": "firecrawl",
        }

    def research_company(
        self,
        company_name: str,
        company_domain: str,
        max_results: int = 20,
    ) -> list[dict[str, Any]]:
        """Find official pages, company announcements, and recent news."""

        queries = [
            f"site:{company_domain} about products solutions industries customers",
            f"site:{company_domain} news press release partnership funding expansion",
            f'"{company_name}" latest news funding partnership expansion product launch',
        ]
        documents: dict[str, dict[str, Any]] = {}
        per_query = max(2, min(5, max_results // len(queries)))

        for query in queries:
            response = self.client.search(
                query=query,
                sources=["web", "news"],
                limit=per_query,
                scrape_options={"formats": ["markdown"]},
            )
            for source_type in ("web", "news"):
                for item in self._get(response, source_type, []) or []:
                    normalized = self._normalize(item, source_type)
                    if normalized["url"] and normalized["content"]:
                        documents[normalized["url"]] = normalized

        return list(documents.values())[:max_results]
