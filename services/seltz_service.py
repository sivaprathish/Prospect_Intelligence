"""Seltz service for market research and public people discovery."""

from __future__ import annotations

import os
import time
from typing import Any

from seltz import (
    Seltz,
    SeltzAPIError,
    SeltzAuthenticationError,
    SeltzConnectionError,
    SeltzError,
    SeltzRateLimitError,
    SeltzTimeoutError,
)


class SeltzService:
    def __init__(
        self,
        api_key: str | None = None,
        max_retries: int = 3,
    ) -> None:
        key = api_key or os.getenv("SELTZ_API_KEY")

        if not key:
            raise ValueError("SELTZ_API_KEY is missing")

        self.client = Seltz(api_key=key)
        self.max_retries = max_retries

    def _search(
        self,
        query: str,
        max_results: int,
    ) -> Any:
        """Run a Seltz search with retry handling."""

        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                print(
                    f"Seltz search attempt "
                    f"{attempt}/{self.max_retries}..."
                )

                return self.client.search(
                    query=query,
                    max_results=max_results,
                )

            except SeltzAuthenticationError as error:
                raise RuntimeError(
                    "Invalid SELTZ_API_KEY"
                ) from error

            except (
                SeltzTimeoutError,
                SeltzConnectionError,
                SeltzRateLimitError,
            ) as error:
                last_error = error

            except SeltzAPIError as error:
                message = str(error).lower()

                transient_words = (
                    "timeout",
                    "deadline",
                    "unavailable",
                    "temporarily",
                )

                if not any(
                    word in message
                    for word in transient_words
                ):
                    raise RuntimeError(
                        f"Seltz API error: {error}"
                    ) from error

                last_error = error

            except SeltzError as error:
                raise RuntimeError(
                    f"Seltz search failed: {error}"
                ) from error

            if attempt < self.max_retries:
                wait_seconds = 2 ** (attempt - 1)
                time.sleep(wait_seconds)

        raise RuntimeError(
            "Seltz search failed after retries"
        ) from last_error

    @staticmethod
    def _normalize_document(
        document: Any,
        source_type: str,
    ) -> dict[str, Any] | None:
        url = getattr(document, "url", None)
        content = getattr(document, "content", "") or ""

        if not url or not content:
            return None

        return {
            "url": url,
            "content": content,
            "published_date": getattr(
                document,
                "published_date",
                None,
            ),
            "source_type": source_type,
            "source_provider": "seltz",
        }

    def research_market(
        self,
        company_name: str,
        company_domain: str,
        max_results: int = 12,
    ) -> list[dict[str, Any]]:
        """Research company, market, industry and competitors."""

        queries = [
            (
                f'"{company_name}" company industry '
                "products customers competitors"
            ),
            (
                f'"{company_name}" challenges risks '
                "growth strategy market"
            ),
            (
                f'"{company_name}" competitors '
                "industry trends"
            ),
        ]

        per_query = max(
            2,
            min(5, max_results // len(queries)),
        )

        documents: dict[str, dict[str, Any]] = {}

        for query in queries:
            response = self._search(
                query=query,
                max_results=per_query,
            )

            for document in response.documents:
                normalized = self._normalize_document(
                    document,
                    source_type="external_web",
                )

                if normalized:
                    documents[normalized["url"]] = normalized

        return list(documents.values())[:max_results]

    def search_people(
        self,
        company_name: str,
        company_domain: str,
        opportunity_titles: list[str] | None = None,
        max_results: int = 15,
    ) -> list[dict[str, Any]]:
        """Find public evidence for current decision-makers."""

        opportunities = ", ".join(
            opportunity_titles or []
        )

        queries = [
            (
                f'site:linkedin.com/in "{company_name}" '
                'CEO OR CTO OR CIO OR VP OR Director OR "Head of"'
            ),
            (
                f'"{company_name}" leadership team '
                f'executives directors "{company_domain}"'
            ),
            (
                f'"{company_name}" decision makers '
                f'"{opportunities}" current role biography'
            ),
        ]

        per_query = max(
            2,
            min(5, max_results // len(queries)),
        )

        documents: dict[str, dict[str, Any]] = {}

        for query in queries:
            response = self._search(
                query=query,
                max_results=per_query,
            )

            for document in response.documents:
                normalized = self._normalize_document(
                    document,
                    source_type="professional_profile",
                )

                if normalized:
                    documents[normalized["url"]] = normalized

        return list(documents.values())[:max_results]