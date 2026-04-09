from __future__ import annotations

from datetime import UTC, datetime

import requests

from ..models import AppResult, MatchEvidence, ReleaseInfo, SourceAttribution
from .base import BaseScanner


class GithubCodeScanner(BaseScanner):
    name = "github_code"
    source_type = "github_repo"
    trust_level = "high"

    def __init__(self, token: str, process_count: int = 4):
        self.token = token
        self.process_count = process_count
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"token {token}", "Accept": "application/vnd.github+json"})

    def find_matching_apps(self) -> list[AppResult]:
        query = '"rikka.shizuku" language:Java OR language:Kotlin'
        response = self.session.get(
            "https://api.github.com/search/code",
            params={"q": query, "per_page": 20},
            timeout=30,
        )
        response.raise_for_status()
        items = response.json().get("items", [])

        apps: list[AppResult] = []
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
                    match_reasons=["Matched GitHub code search for rikka.shizuku"],
                    evidence=[
                        MatchEvidence(
                            source=self.name,
                            reason="github-code-search",
                            detail=item.get("path"),
                            file_path=item.get("path"),
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
