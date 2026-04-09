from __future__ import annotations

from .models import AppResult


def score_apps(apps: list[AppResult], scoring_rules: dict[str, list[str]]) -> list[AppResult]:
    high_markers = [m.lower() for m in scoring_rules.get("confidence_high_markers", [])]
    medium_markers = [m.lower() for m in scoring_rules.get("confidence_medium_markers", [])]

    for app in apps:
        joined = " ".join(app.match_reasons + [ev.reason for ev in app.evidence]).lower()
        if any(marker in joined for marker in high_markers):
            app.confidence = "high"
        elif any(marker in joined for marker in medium_markers):
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
