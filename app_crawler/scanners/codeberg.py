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
            release_info, enriched_desc, urls = self._enrich_repo(repo)
            apps.append(
                AppResult(
                    name=repo.get("name", "unknown"),
                    urls=urls,
                    scanner=self.name,
                    desc=enriched_desc,
                    last_updated=_parse_datetime(repo.get("updated_at")),
                    has_downloads=release_info.has_downloads,
                    match_reasons=["Matched Codeberg repository metadata for Shizuku-related terms"],
                    evidence=[MatchEvidence(source=self.name, reason="codeberg-repo-search", detail=full_name, file_path="repository metadata")],
                    sources=[SourceAttribution(scanner=self.name, source_type=self.source_type, trust_level=self.trust_level)],
                    release_info=release_info,
                )
            )
        return apps

    def _enrich_repo(self, repo: dict) -> tuple[ReleaseInfo, str | None, list[str]]:
        full_name = repo.get("full_name") or ""
        description = repo.get("description") or None
        urls = [u for u in [repo.get("html_url"), repo.get("website")] if u]
        if not full_name or '/' not in full_name:
            return ReleaseInfo(), description, sorted(dict.fromkeys(urls))
        owner, name = full_name.split('/', 1)
        release_info = ReleaseInfo()

        releases_resp = self.session.get(f"{self.base_url}/repos/{owner}/{name}/releases", params={"limit": 1}, timeout=30)
        if releases_resp.status_code == 200:
            releases = releases_resp.json()
            if releases:
                rel = releases[0]
                assets = rel.get("assets") or []
                asset_names = [asset.get("name", "") for asset in assets if asset.get("name")]
                release_info = ReleaseInfo(
                    has_downloads=bool(asset_names),
                    release_url=rel.get("html_url") or rel.get("url"),
                    release_tag=rel.get("tag_name"),
                    release_published_at=rel.get("published_at") or rel.get("created_at"),
                    apk_assets=[name for name in asset_names if name.lower().endswith('.apk')],
                    aab_assets=[name for name in asset_names if name.lower().endswith('.aab')],
                    quality_label='installable' if any(name.lower().endswith(('.apk', '.aab')) for name in asset_names) else ('assets_only' if asset_names else 'unknown'),
                )

        tags_resp = self.session.get(f"{self.base_url}/repos/{owner}/{name}/tags", params={"limit": 1}, timeout=30)
        if tags_resp.status_code == 200:
            tags = tags_resp.json()
            if tags and not release_info.release_tag:
                tag = tags[0]
                release_info.release_tag = tag.get("name")
                release_info.release_published_at = release_info.release_published_at or tag.get("commit", {}).get("created")

        if release_info.release_url and release_info.release_url not in urls:
            urls.append(release_info.release_url)

        enriched_parts = [description] if description else []
        if release_info.release_tag:
            enriched_parts.append(f"latest tag: {release_info.release_tag}")
        if repo.get("stars_count") is not None:
            enriched_parts.append(f"stars: {repo.get('stars_count')}")
        return release_info, " | ".join(part for part in enriched_parts if part) or None, sorted(dict.fromkeys(urls))


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except Exception:
        return None
