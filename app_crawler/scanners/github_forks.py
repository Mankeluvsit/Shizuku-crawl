from __future__ import annotations

from datetime import UTC, datetime

import requests

from ..models import AppResult, ForkLineage, MatchEvidence, ReleaseInfo, SourceAttribution
from ..release_assets import classify_release_assets
from .base import BaseScanner


class GithubForksScanner(BaseScanner):
    name = "github_forks"
    source_type = "github_fork"
    trust_level = "medium"

    def __init__(self, token: str, process_count: int = 4):
        self.token = token
        self.process_count = process_count
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"token {token}", "Accept": "application/vnd.github+json"})

    def find_matching_apps(self) -> list[AppResult]:
        response = self.session.get(
            "https://api.github.com/search/repositories",
            params={"q": "shizuku fork:true in:name,description,readme", "sort": "updated", "per_page": 20},
            timeout=30,
        )
        response.raise_for_status()
        items = response.json().get("items", [])

        apps: list[AppResult] = []
        for repo in items:
            if not repo.get("fork"):
                continue
            html_url = repo.get("html_url")
            full_name = repo.get("full_name", "")
            if not html_url or not full_name:
                continue
            release_info = self._fetch_release_info(full_name)
            parent = self._fetch_parent_name(full_name)
            lineage = self._fetch_fork_lineage(full_name, parent)
            desc = repo.get("description") or ""
            if parent:
                desc = (desc + f" | fork of {parent}").strip(" |")
            apps.append(
                AppResult(
                    name=repo.get("name", "unknown"),
                    urls=[html_url],
                    scanner=self.name,
                    desc=desc or None,
                    last_updated=_parse_datetime(repo.get("updated_at")),
                    has_downloads=release_info.has_downloads,
                    match_reasons=["Matched active GitHub fork for Shizuku-related repository"],
                    evidence=[
                        MatchEvidence(
                            source=self.name,
                            reason="github-fork-scan",
                            detail=full_name,
                            file_path=parent or "fork metadata",
                        )
                    ],
                    sources=[SourceAttribution(scanner=self.name, source_type=self.source_type, trust_level=self.trust_level)],
                    release_info=release_info,
                    fork_lineage=lineage,
                )
            )
        return apps

    def _fetch_release_info(self, full_name: str) -> ReleaseInfo:
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

    def _fetch_parent_name(self, full_name: str) -> str | None:
        response = self.session.get(f"https://api.github.com/repos/{full_name}", timeout=30)
        if response.status_code != 200:
            return None
        parent = response.json().get("parent") or {}
        return parent.get("full_name")

    def _fetch_fork_lineage(self, full_name: str, parent_full_name: str | None) -> ForkLineage:
        if not parent_full_name:
            return ForkLineage()
        response = self.session.get(
            f"https://api.github.com/repos/{full_name}/compare/{parent_full_name.split('/')[-1]}...HEAD",
            timeout=30,
        )
        if response.status_code != 200:
            return ForkLineage(parent_full_name=parent_full_name)
        data = response.json()
        ahead_by = int(data.get("ahead_by", 0) or 0)
        behind_by = int(data.get("behind_by", 0) or 0)
        return ForkLineage(
            parent_full_name=parent_full_name,
            ahead_by=ahead_by,
            behind_by=behind_by,
            is_meaningfully_ahead=ahead_by >= 3,
        )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except Exception:
        return None
