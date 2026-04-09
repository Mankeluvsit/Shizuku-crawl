from __future__ import annotations

from datetime import UTC, datetime

from ..http import build_retry_session
from ..models import AppResult, MatchEvidence, ReleaseInfo, SourceAttribution
from ..release_assets import classify_release_assets
from .base import BaseScanner
from .discovery import (
    BROAD_GITHUB_REPO_EXTRA_QUERIES,
    STRICT_GITHUB_REPO_QUERIES,
    expand_queries,
    paginated_search_items,
)


class GithubMetaScanner(BaseScanner):
    name = "github_meta"
    source_type = "github_repo"
    trust_level = "medium"

    def __init__(self, token: str, process_count: int = 4, discovery_mode: str = 'strict', search_pages: int = 1):
        self.token = token
        self.process_count = process_count
        self.discovery_mode = discovery_mode
        self.search_pages = max(1, search_pages)
        self.session = build_retry_session()
        self.session.headers.update({"Authorization": f"token {token}", "Accept": "application/vnd.github+json"})

    def find_matching_apps(self) -> list[AppResult]:
        queries = expand_queries(self.discovery_mode, STRICT_GITHUB_REPO_QUERIES, BROAD_GITHUB_REPO_EXTRA_QUERIES)
        apps: list[AppResult] = []
        for query in queries:
            items = paginated_search_items(
                self.session,
                "https://api.github.com/search/repositories",
                query=query,
                per_page=20,
                pages=self.search_pages,
                timeout=30,
            )
            for repo in items:
                html_url = repo.get("html_url")
                if not html_url:
                    continue

                release_info = self._fetch_release_info(repo.get("full_name", ""))
                apps.append(
                    AppResult(
                        name=repo.get("name", "unknown"),
                        urls=[html_url],
                        scanner=self.name,
                        desc=repo.get("description"),
                        last_updated=_parse_datetime(repo.get("updated_at")),
                        has_downloads=release_info.has_downloads,
                        match_reasons=[f"Matched GitHub repository metadata query: {query}"],
                        evidence=[
                            MatchEvidence(
                                source=self.name,
                                reason="github-repository-search",
                                detail=f"{query} :: {repo.get('full_name')}",
                                file_path="README or metadata",
                            )
                        ],
                        sources=[SourceAttribution(scanner=self.name, source_type=self.source_type, trust_level=self.trust_level)],
                        release_info=release_info,
                    )
                )
        return apps

    def _fetch_release_info(self, full_name: str) -> ReleaseInfo:
        if not full_name:
            return ReleaseInfo()
        response = self.session.get(f"https://api.github.com/repos/{full_name}/releases/latest", timeout=30)
        if response.status_code != 200:
            return ReleaseInfo()
        data = response.json()
        assets = data.get("assets", [])
        asset_names = [asset.get("name", "") for asset in assets if asset.get("name")]
        return classify_release_assets(
            asset_names,
            release_url=data.get("html_url"),
            release_tag=data.get("tag_name"),
            release_published_at=data.get("published_at"),
        )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except Exception:
        return None
