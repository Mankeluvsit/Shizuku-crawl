from __future__ import annotations

from .models import AppResult


HIGH_MARKERS = ["rikka.shizuku", "fdroid-metadata"]
MEDIUM_MARKERS = ["shizuku"]


def score_apps(apps: list[AppResult]) -> list[AppResult]:
    for app in apps:
        joined = " ".join(app.match_reasons + [ev.reason for ev in app.evidence]).lower()
        if any(marker in joined for marker in HIGH_MARKERS):
            app.confidence = "high"
        elif any(marker in joined for marker in MEDIUM_MARKERS):
            app.confidence = "medium"
        else:
            app.confidence = "low"

        if app.has_downloads or app.release_info.has_downloads:
            app.usefulness = "high"
        elif app.last_updated is not None:
            app.usefulness = "medium"
        else:
            app.usefulness = "low"
    return apps
