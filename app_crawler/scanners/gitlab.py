from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import quote_plus

from ..http import build_retry_session
from ..models import AppResult, MatchEvidence, ReleaseInfo, SourceAttribution
from .base import BaseScanner


class GitLabScanner(BaseScanner):
    name = "gitlab"
    source_type = "gitlab_project"
    trust_level = "medium"

    def __init__(self):
        self.session = build_retry_session()
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
            release_info, enriched_desc, urls = self._enrich_project(project)
            apps.append(
                AppResult(
                    name=project.get("name", "unknown"),
                    urls=urls,
                    scanner=self.name,
                    desc=enriched_desc,
                    last_updated=_parse_datetime(project.get("last_activity_at")),
                    has_downloads=release_info.has_downloads,
                    match_reasons=["Matched GitLab project metadata for Shizuku-related terms"],
                    evidence=[MatchEvidence(source=self.name, reason="gitlab-project-search", detail=namespace, file_path="project metadata")],
                    sources=[SourceAttribution(scanner=self.name, source_type=self.source_type, trust_level=self.trust_level)],
                    release_info=release_info,
                )
            )
        return apps

    def _enrich_project(self, project: dict) -> tuple[ReleaseInfo, str | None, list[str]]:
        project_id = project.get("id")
        description = project.get("description") or None
        urls = [u for u in [project.get("web_url"), project.get("homepage")] if u]
        if not project_id:
            return ReleaseInfo(), description, sorted(dict.fromkeys(urls))

        release_info = ReleaseInfo()

        releases_resp = self.session.get(f"{self.base_url}/projects/{project_id}/releases", params={"per_page": 1}, timeout=30)
        if releases_resp.status_code == 200:
            releases = releases_resp.json()
            if releases:
                rel = releases[0]
                assets = rel.get("assets") or {}
                links = assets.get("links") or []
                asset_names = [link.get("name", "") for link in links if link.get("name")]
                release_info = ReleaseInfo(
                    has_downloads=bool(asset_names),
                    release_url=rel.get("_links", {}).get("self") or rel.get("url"),
                    release_tag=rel.get("tag_name"),
                    release_published_at=rel.get("released_at") or rel.get("created_at"),
                    apk_assets=[name for name in asset_names if name.lower().endswith('.apk')],
                    aab_assets=[name for name in asset_names if name.lower().endswith('.aab')],
                    quality_label='installable' if any(name.lower().endswith(('.apk', '.aab')) for name in asset_names) else ('assets_only' if asset_names else 'unknown'),
                )

        tags_resp = self.session.get(f"{self.base_url}/projects/{project_id}/repository/tags", params={"per_page": 1}, timeout=30)
        if tags_resp.status_code == 200:
            tags = tags_resp.json()
            if tags and not release_info.release_tag:
                tag = tags[0]
                release_info.release_tag = tag.get("name")
                release_info.release_published_at = release_info.release_published_at or tag.get("commit", {}).get("created_at")

        homepage = project.get("web_url")
        if homepage and homepage not in urls:
            urls.append(homepage)
        if release_info.release_url and release_info.release_url not in urls:
            urls.append(release_info.release_url)

        enriched_parts = [description] if description else []
        if release_info.release_tag:
            enriched_parts.append(f"latest tag: {release_info.release_tag}")
        if project.get("star_count") is not None:
            enriched_parts.append(f"stars: {project.get('star_count')}")
        return release_info, " | ".join(part for part in enriched_parts if part) or None, sorted(dict.fromkeys(urls))


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except Exception:
        return None
