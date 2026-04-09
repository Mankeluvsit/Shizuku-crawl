from __future__ import annotations

from datetime import UTC, datetime

from ..http import build_retry_session
from ..models import AppResult, MatchEvidence, ReleaseInfo, SourceAttribution
from .base import BaseScanner


class CodebergScanner(BaseScanner):
    name = "codeberg"
    source_type = "codeberg_repo"
    trust_level = "medium"

    def __init__(self):
        self.session = build_retry_session()
        self.base_url = "https://codeberg.org/api/v1"

    def find_matching_apps(self) -> list[AppResult]:
        response = self.session.get(
            f"{self.base_url}/repos/search",
            params={"q": "shizuku", "limit": 20},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        items = data.get("data") or data if isinstance(data, list) else []
        apps: list[AppResult] = []
        for repo in items:
            full_name = repo.get("full_name") or ""
            html_url = repo.get("html_url")
            if not full_name or not html_url:
                continue
            text = " ".join(filter(None, [repo.get("name"), repo.get("description"), full_name])).lower()
            if "shizuku" not in text:
                continue
            apps.append(
                AppResult(
                    name=repo.get("name", "unknown"),
                    urls=[html_url],
                    scanner=self.name,
                    desc=repo.get("description"),
                    last_updated=_parse_datetime(repo.get("updated_at")),
                    match_reasons=["Matched Codeberg repository metadata for Shizuku-related terms"],
                    evidence=[MatchEvidence(source=self.name, reason="codeberg-repo-search", detail=full_name, file_path="repository metadata")],
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
