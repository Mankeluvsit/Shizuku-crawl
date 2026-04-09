from __future__ import annotations

from .models import AppResult
from .utils import normalize_url


def normalize_app(app: AppResult) -> AppResult:
    app.urls = [normalize_url(url) for url in app.urls if url]
    app.urls = sorted(dict.fromkeys(app.urls))
    if app.package_id:
        app.package_id = app.package_id.strip()
    if app.application_id:
        app.application_id = app.application_id.strip()
    if app.name:
        app.name = app.name.strip()
    if app.desc:
        app.desc = " ".join(app.desc.split())
    return app


def normalize_apps(apps: list[AppResult]) -> list[AppResult]:
    return [normalize_app(app) for app in apps]
