from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

from .cache import Cache
from .config import AppConfig
from .known import filter_known_apps
from .models import AppResult, ReviewState
from .normalize import normalize_apps
from .outputs import write_csv, write_diff, write_html, write_json, write_stats, write_summary
from .rules import apply_aliases, load_rule_set, should_force_include, should_ignore
from .scanners.fdroid import FDroidScanner
from .scanners.github_code import GithubCodeScanner
from .scanners.github_meta import GithubMetaScanner
from .scanners.github_releases import GithubReleasesScanner
from .scanners.github_forks import GithubForksScanner
from .scoring import score_apps


def _setup_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format="%(levelname)s: %(message)s")


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
    scanners = [
        FDroidScanner("https://f-droid.org/repo/index.xml"),
        FDroidScanner("https://apt.izzysoft.de/fdroid/repo/index.xml"),
    ]

    if config.github_auth:
        scanners.extend(
            [
                GithubCodeScanner(config.github_auth, process_count=config.process_count),
                GithubMetaScanner(config.github_auth, process_count=config.process_count),
                GithubReleasesScanner(config.github_auth, process_count=config.process_count),
                GithubForksScanner(config.github_auth, process_count=config.process_count),
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


def _apply_review_state(apps: list[AppResult], review_state: dict[str, ReviewState]) -> None:
    for app in apps:
        app.apply_review_state(review_state.get(app.identity_key_str()))


def _filter_incremental(current_apps: list[AppResult], previous_apps: list[AppResult]) -> list[AppResult]:
    previous_map = {app.identity_key(): app.to_dict() for app in previous_apps}
    changed: list[AppResult] = []
    for app in current_apps:
        previous = previous_map.get(app.identity_key())
        if previous is None or previous != app.to_dict():
            changed.append(app)
    return changed


def run_pipeline(config: AppConfig) -> None:
    _setup_logging(config.log_level)

    cwd = Path.cwd()
    cache_dir = cwd / "cache"
    cache = Cache(cache_dir)
    rule_set = load_rule_set(config.rules_dir)

    previous_apps = [] if config.no_cache else cache.load_all()
    existing_review_state = cache.load_review_state()

    current_apps = _scan_apps(config)
    current_apps = normalize_apps(current_apps)
    current_apps = apply_aliases(current_apps, rule_set.aliases)
    current_apps = filter_known_apps(current_apps, config.target_path)

    filtered_current: list[AppResult] = []
    for app in current_apps:
        if should_ignore(app, rule_set):
            continue
        filtered_current.append(app)
    current_apps = filtered_current

    now = datetime.now(UTC).isoformat()
    for app in current_apps:
        if not app.first_seen:
            app.first_seen = now
        app.last_seen = now

    merged = _dedupe_apps([*current_apps, *previous_apps])
    merged = apply_aliases(merged, rule_set.aliases)
    merged = filter_known_apps(merged, config.target_path)
    merged = [app for app in merged if not should_ignore(app, rule_set) or should_force_include(app, rule_set)]
    merged = score_apps(merged, rule_set.scoring_rules)
    _apply_review_state(merged, existing_review_state)
    merged.sort(key=lambda a: a.name.casefold())

    if config.dry_run:
        logging.info("Dry run: %d app(s) would be written", len(merged))
        for app in merged[:20]:
            logging.info("%s -> %s", app.name, app.urls[:1])
        return

    report_apps = _filter_incremental(merged, previous_apps) if config.incremental else merged

    summary_path = cwd / config.summary_file
    stats_path = cwd / config.stats_file
    diff_path = cwd / config.diff_file

    write_summary(summary_path, report_apps, config.recent_days)
    write_stats(stats_path, report_apps)
    write_diff(diff_path, merged, previous_apps)

    if config.write_json:
        write_json(cwd / "apps.json", report_apps)
    if config.write_csv:
        write_csv(cwd / "apps.csv", report_apps)
    if config.write_html:
        write_html(cwd / "apps.html", report_apps)

    cache.save_current_run(merged)
    cache.save_review_state({app.identity_key_str(): app.to_review_state() for app in merged})

    logging.info("Wrote %d app(s) to reports", len(report_apps))
    for app in report_apps:
        logging.info("%s: %s %s", app.scanner, app.name, app.urls)
