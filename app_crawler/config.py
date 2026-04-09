from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    target_path: Path
    github_auth: str | None
    summary_file: str
    stats_file: str
    diff_file: str
    write_json: bool
    write_csv: bool
    write_html: bool
    dry_run: bool
    no_cache: bool
    incremental: bool
    preset: str
    discovery_mode: str = "strict"
    search_pages: int = 1
    webui: bool = False
    webui_host: str = "127.0.0.1"
    webui_port: int = 8765
    process_count: int = 1
    recent_days: int = 90
    log_level: str = "INFO"
    rules_dir: Path = Path("rules")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover Shizuku-related apps and repositories.")
    parser.add_argument("target_path", nargs="?", default=".", help="Path containing markdown/readme files to compare against")
    parser.add_argument("--summary-file", default=os.getenv("SUMMARY_FILE", "SUMMARY.md"))
    parser.add_argument("--stats-file", default="scan_stats.json")
    parser.add_argument("--diff-file", default="scan_diff.json")
    parser.add_argument("--json", action="store_true", dest="write_json", help="Write apps.json")
    parser.add_argument("--csv", action="store_true", dest="write_csv", help="Write apps.csv")
    parser.add_argument("--html", action="store_true", dest="write_html", help="Write apps.html")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--incremental", action="store_true", help="Write reports only for new or changed apps compared with the previous cached run")
    parser.add_argument("--preset", default=os.getenv("SCAN_PRESET", "full"), choices=["full", "quick", "github-only", "fdroid-only", "non-github"], help="Scanner preset selection")
    parser.add_argument("--discovery-mode", default=os.getenv("DISCOVERY_MODE", "strict"), choices=["strict", "broad"], help="Use strict verified-style discovery or broader recall-oriented discovery")
    parser.add_argument("--search-pages", type=int, default=int(os.getenv("SEARCH_PAGES", "1")), help="How many result pages to fetch per discovery query")
    parser.add_argument("--webui", action="store_true", help="Start the built-in Web UI review dashboard")
    parser.add_argument("--webui-host", default=os.getenv("WEBUI_HOST", "127.0.0.1"))
    parser.add_argument("--webui-port", type=int, default=int(os.getenv("WEBUI_PORT", "8765")))
    parser.add_argument("--rules-dir", default="rules")
    parser.add_argument(
        "--process-count",
        type=int,
        default=int(os.getenv("PROCESS_COUNT", max(1, (os.cpu_count() or 2) - 1))),
    )
    parser.add_argument("--recent-days", type=int, default=int(os.getenv("RECENT_DAYS", "90")))
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    return parser


def config_from_args(args: argparse.Namespace) -> AppConfig:
    github_auth = os.getenv("GITHUB_AUTH")
    return AppConfig(
        target_path=Path(args.target_path).resolve(),
        github_auth=github_auth if github_auth else None,
        summary_file=args.summary_file,
        stats_file=args.stats_file,
        diff_file=args.diff_file,
        write_json=args.write_json,
        write_csv=args.write_csv,
        write_html=args.write_html,
        dry_run=args.dry_run,
        no_cache=args.no_cache,
        incremental=args.incremental,
        preset=str(args.preset),
        discovery_mode=str(args.discovery_mode),
        search_pages=max(1, int(args.search_pages)),
        webui=bool(args.webui),
        webui_host=str(args.webui_host),
        webui_port=int(args.webui_port),
        process_count=max(1, args.process_count),
        recent_days=max(1, args.recent_days),
        log_level=str(args.log_level).upper(),
        rules_dir=Path(args.rules_dir).resolve(),
    )
