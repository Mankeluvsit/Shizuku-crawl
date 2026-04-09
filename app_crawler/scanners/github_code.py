from __future__ import annotations

import logging
from datetime import UTC, datetime

import requests

from ..http import build_retry_session
from ..models import AppResult, MatchEvidence, ReleaseInfo, SourceAttribution
from .base import BaseScanner
from .discovery import (
    BROAD_GITHUB_CODE_EXTRA_QUERIES,
    STRICT_GITHUB_CODE_QUERIES,
    classify_github_code_query,
    expand_queries,
    paginated_search_items,
)


class GithubCodeScanner(BaseScanner):
    name = "github_code"
    source_type = "github_repo"
    trust_level = "high"

    def __init__(self, token: str, process_count: int = 4, discovery_mode: str = 'strict', search_pages: int = 1):
        self.token = token
        self.process_count = process_count
        self.discovery_mode = discovery_mode
        self.search_pages = max(1, search_pages)
        self.session = build_retry_session()
        self.session.headers.update({"Authorization": f"token {token}", "Accept": "application/vnd.github+json"})

    def find_matching_apps(self) -> list[AppResult]:
        queries = expand_queries(self.discovery_mode, STRICT_GITHUB_CODE_QUERIES, BROAD_GITHUB_CODE_EXTRA_QUERIES)
        apps: list[AppResult] = []
        for query in queries:
            evidence_strength = classify_github_code_query(query)
            try:
                items = paginated_search_items(
                    self.session,
                    "https://api.github.com/search/code",
                    query=query,
                    per_page=20,
                    pages=self.search_pages,
                    timeout=30,
                )
            except requests.HTTPError as exc:
                status_code = getattr(getattr(exc, 'response', None), 'status_code', None)
                if status_code == 403:
                    logging.warning(
                        "github_code search forbidden for query %r; skipping remaining code-search queries. Configure GH_PAT for Actions or reduce broad code-search usage.",
                        query,
                    )
                    break
                raise
            for item in items:
                repository = item.get("repository", {})
                html_url = repository.get("html_url")
                full_name = repository.get("full_name") or ""
                if not html_url:
                    continue
                apps.append(
                    AppResult(
                        name=repository.get("name", full_name.split("/")[-1]),
                        urls=[html_url],
                        scanner=self.name,
                        desc=repository.get("description"),
                        last_updated=_parse_datetime(repository.get("updated_at")),
                        match_reasons=[f"Matched GitHub code search query: {query}"],
                        evidence=[
                            MatchEvidence(
                                source=self.name,
                                reason="github-code-search",
                                detail=f"{query} :: {item.get('path')}",
                                file_path=item.get("path"),
                                evidence_strength=evidence_strength,
                            )
                        ],
                        sources=[SourceAttribution(scanner=self.name, source_type=self.source_type, trust_level=self.trust_level)],
                        release_info=ReleaseInfo(has_downloads=False),
                    )
                )
        return apps


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except Exception:
        return None
