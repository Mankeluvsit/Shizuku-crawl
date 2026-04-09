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

        quality = (app.release_info.quality_label or "unknown").lower()
        has_checksum = bool(app.release_info.checksum_assets)
        has_universal = bool(app.release_info.universal_apk_assets)
        meaningfully_ahead = bool(app.fork_lineage.is_meaningfully_ahead)
        has_recent_update = app.last_updated is not None
        has_release_hint = bool(app.release_info.release_tag or app.release_info.release_url)

        if quality == "strong" or (has_universal and has_checksum):
            app.usefulness = "high"
        elif quality == "installable":
            app.usefulness = "high" if meaningfully_ahead or has_recent_update else "medium"
        elif (app.has_downloads or app.release_info.has_downloads) and has_release_hint:
            app.usefulness = "medium"
        elif meaningfully_ahead and has_recent_update:
            app.usefulness = "medium"
        elif has_recent_update:
            app.usefulness = "medium"
        else:
            app.usefulness = "low"
    return apps
