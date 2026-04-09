from __future__ import annotations

from datetime import UTC, datetime

import requests

from ..models import AppResult, MatchEvidence, ReleaseInfo, SourceAttribution
from .base import BaseScanner


class GithubReleasesScanner(BaseScanner):
    name = "github_releases"
    source_type = "github_release"
    trust_level = "high"

    def __init__(self, token: str, process_count: int = 4):
        self.token = token
        self.process_count = process_count
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"token {token}", "Accept": "application/vnd.github+json"})

    def find_matching_apps(self) -> list[AppResult]:
        response = self.session.get(
            "https://api.github.com/search/repositories",
            params={"q": "shizuku in:name,description,readme", "sort": "updated", "per_page": 20},
            timeout=30,
        )
        response.raise_for_status()
        items = response.json().get("items", [])

        apps: list[AppResult] = []
        for repo in items:
            full_name = repo.get("full_name", "")
            if not full_name:
                continue
            release_info = self._fetch_release_info(full_name)
            if not release_info.release_url:
                continue
            html_url = repo.get("html_url")
            if not html_url:
                continue
            apps.append(
                AppResult(
                    name=repo.get("name", "unknown"),
                    urls=[html_url],
                    scanner=self.name,
                    desc=repo.get("description"),
                    last_updated=_parse_datetime(repo.get("updated_at")),
                    has_downloads=release_info.has_downloads,
                    match_reasons=["Matched GitHub releases for Shizuku-related repository"],
                    evidence=[
                        MatchEvidence(
                            source=self.name,
                            reason="github-release-scan",
                            detail=full_name,
                            file_path="releases/latest",
                        )
                    ],
                    sources=[SourceAttribution(scanner=self.name, source_type=self.source_type, trust_level=self.trust_level)],
                    release_info=release_info,
                )
            )
        return apps

    def _fetch_release_info(self, full_name: str) -> ReleaseInfo:
        response = self.session.get(f"https://api.github.com/repos/{full_name}/releases/latest", timeout=30)
        if response.status_code != 200:
            return ReleaseInfo()
        data = response.json()
        assets = data.get("assets", [])
        apk_assets = [asset.get("name", "") for asset in assets if asset.get("name", "").lower().endswith((".apk", ".aab"))]
        return ReleaseInfo(
            has_downloads=bool(assets),
            release_url=data.get("html_url"),
            release_tag=data.get("tag_name"),
            release_published_at=data.get("published_at"),
            apk_assets=apk_assets,
        )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except Exception:
        return None
