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
    process_count: int
    recent_days: int
    log_level: str


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
        process_count=max(1, args.process_count),
        recent_days=max(1, args.recent_days),
        log_level=str(args.log_level).upper(),
    )
