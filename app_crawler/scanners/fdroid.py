from __future__ import annotations

from datetime import UTC, datetime
import xml.etree.ElementTree as ET

import requests

from ..models import AppResult, MatchEvidence, ReleaseInfo, SourceAttribution
from .base import BaseScanner


class FDroidScanner(BaseScanner):
    name = "fdroid"
    source_type = "fdroid_repo"
    trust_level = "high"

    def __init__(self, index_url: str):
        self.index_url = index_url

    def find_matching_apps(self) -> list[AppResult]:
        response = requests.get(self.index_url, timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        apps: list[AppResult] = []
        for app in root.findall("application"):
            package_name = (app.findtext("id") or "").strip()
            name = (app.findtext("name") or package_name).strip()
            summary = (app.findtext("summary") or "").strip() or None
            desc = ((app.findtext("desc") or "").strip() or summary)
            web = (app.findtext("web") or "").strip()
            source = (app.findtext("source") or "").strip()
            issue = (app.findtext("tracker") or "").strip()
            release_url = web or source or issue
            categories = " ".join(c.text or "" for c in app.findall("categories/category"))
            body = " ".join(filter(None, [name, summary or "", desc or "", categories, release_url]))

            matched = any(term in body.lower() for term in ["shizuku", "rikka.shizuku"])
            if not matched:
                continue

            last_updated = None
            added = (app.findtext("added") or "").strip()
            if added:
                try:
                    last_updated = datetime.fromisoformat(added.replace("Z", "+00:00")).astimezone(UTC)
                except Exception:
                    last_updated = None

            urls = [u for u in [release_url, source, issue, web] if u]
            if not urls:
                urls = [f"https://f-droid.org/packages/{package_name}/"]

            apps.append(
                AppResult(
                    name=name,
                    urls=urls,
                    scanner=self.name,
                    desc=desc,
                    package_id=package_name or None,
                    last_updated=last_updated,
                    has_downloads=True,
                    match_reasons=["Matched F-Droid metadata for Shizuku-related terms"],
                    evidence=[MatchEvidence(source=self.name, reason="fdroid-metadata", detail=body[:300])],
                    sources=[SourceAttribution(scanner=self.name, source_type=self.source_type, trust_level=self.trust_level)],
                    release_info=ReleaseInfo(has_downloads=True, release_url=urls[0]),
                )
            )

        return apps
