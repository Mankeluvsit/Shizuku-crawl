from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from .cache import Cache
from .config import AppConfig
from .known import filter_known_apps
from .models import AppResult
from .normalize import normalize_apps
from .outputs import (
    write_csv,
    write_diff,
    write_html,
    write_json,
    write_stats,
    write_summary,
)
from .scanners.fdroid import FDroidScanner
from .scanners.github_code import GithubCodeScanner
from .scanners.github_meta import GithubMetaScanner
from .scoring import score_apps


def _setup_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format="%(levelname)s: %(message)s")


def _is_allowed_app(app: AppResult, ignore_items: set[str]) -> bool:
    if app.name in ignore_items:
        return False
    if any(url in ignore_items for url in app.urls):
        return False
    return True


def _load_ignore_list(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def _dedupe_apps(apps: list[AppResult]) -> list[AppResult]:
    merged: dict[tuple[str, str], AppResult] = {}
    for app in apps:
        key = app.identity_key()
        if key in merged:
            merged[key] = merged[key].merge(app)
        else:
            merged[key] = app
    return list(merged.values())


def _scan_apps(config: AppConfig) -> list[AppResult]:
    apps: list[AppResult] = []

    scanners = [
        FDroidScanner("https://f-droid.org/repo/index.xml"),
        FDroidScanner("https://apt.izzysoft.de/fdroid/repo/index.xml"),
    ]

    if config.github_auth:
        scanners.extend(
            [
                GithubCodeScanner(config.github_auth, process_count=config.process_count),
                GithubMetaScanner(config.github_auth, process_count=config.process_count),
            ]
        )
    else:
        logging.warning("GITHUB_AUTH not set; GitHub scanners will be skipped")

    all_apps: list[AppResult] = []
    for scanner in scanners:
        try:
            found = scanner.find_matching_apps()
            logging.info("%s found %d app(s)", scanner.name, len(found))
            all_apps.extend(found)
        except Exception as exc:
            logging.error("scanner %s failed: %s", scanner.name, exc)

    return all_apps


def run_pipeline(config: AppConfig) -> None:
    _setup_logging(config.log_level)

    cwd = Path.cwd()
    cache_dir = cwd / "cache"
    cache = Cache(cache_dir)

    previous_apps = [] if config.no_cache else cache.load_all()
    current_apps = _scan_apps(config)
    current_apps = normalize_apps(current_apps)
    current_apps = filter_known_apps(current_apps, config.target_path)

    ignore_items = _load_ignore_list(cwd / "ignore_list.lst")
    current_apps = [app for app in current_apps if _is_allowed_app(app, ignore_items)]

    now = datetime.now(UTC).isoformat()
    for app in current_apps:
        if not app.first_seen:
            app.first_seen = now
        app.last_seen = now

    merged = _dedupe_apps([*current_apps, *previous_apps])
    merged = filter_known_apps(merged, config.target_path)
    merged = [app for app in merged if _is_allowed_app(app, ignore_items)]
    merged = score_apps(merged)
    merged.sort(key=lambda a: a.name.casefold())

    if config.dry_run:
        logging.info("Dry run: %d app(s) would be written", len(merged))
        for app in merged[:20]:
            logging.info("%s -> %s", app.name, app.urls[:1])
        return

    summary_path = cwd / config.summary_file
    stats_path = cwd / config.stats_file
    diff_path = cwd / config.diff_file

    write_summary(summary_path, merged, config.recent_days)
    write_stats(stats_path, merged)
    write_diff(diff_path, merged, previous_apps)

    if config.write_json:
        write_json(cwd / "apps.json", merged)
    if config.write_csv:
        write_csv(cwd / "apps.csv", merged)
    if config.write_html:
        write_html(cwd / "apps.html", merged)

    cache.save_current_run(merged)

    for app in merged:
        logging.info("%s: %s %s", app.scanner, app.name, app.urls)
