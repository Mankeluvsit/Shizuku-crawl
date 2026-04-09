from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import quote_plus

import requests

from ..models import AppResult, MatchEvidence, ReleaseInfo, SourceAttribution
from .base import BaseScanner


class GitLabScanner(BaseScanner):
    name = "gitlab"
    source_type = "gitlab_project"
    trust_level = "medium"

    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://gitlab.com/api/v4"

    def find_matching_apps(self) -> list[AppResult]:
        response = self.session.get(
            f"{self.base_url}/projects",
            params={"search": "shizuku", "simple": True, "per_page": 20},
            timeout=30,
        )
        response.raise_for_status()
        items = response.json()
        apps: list[AppResult] = []
        for project in items:
            namespace = project.get("path_with_namespace") or ""
            web_url = project.get("web_url")
            if not namespace or not web_url:
                continue
            text = " ".join(filter(None, [project.get("name"), project.get("description"), namespace])).lower()
            if "shizuku" not in text:
                continue
            apps.append(
                AppResult(
                    name=project.get("name", "unknown"),
                    urls=[web_url],
                    scanner=self.name,
                    desc=project.get("description"),
                    last_updated=_parse_datetime(project.get("last_activity_at")),
                    match_reasons=["Matched GitLab project metadata for Shizuku-related terms"],
                    evidence=[MatchEvidence(source=self.name, reason="gitlab-project-search", detail=namespace, file_path="project metadata")],
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
