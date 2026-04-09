from app_crawler.config import AppConfig
from app_crawler.scanners.registry import build_scanners
from pathlib import Path


def _config(github_auth: str | None):
    return AppConfig(
        target_path=Path('.').resolve(),
        github_auth=github_auth,
        summary_file='SUMMARY.md',
        stats_file='scan_stats.json',
        diff_file='scan_diff.json',
        write_json=False,
        write_csv=False,
        write_html=False,
        dry_run=True,
        no_cache=True,
        incremental=False,
        process_count=1,
        recent_days=90,
        log_level='INFO',
        rules_dir=Path('rules').resolve(),
    )


def test_registry_without_github_auth_skips_github_scanners():
    scanners = build_scanners(_config(None))
    names = {scanner.name for scanner in scanners}
    assert 'fdroid' in names
    assert 'gitlab' in names
    assert 'codeberg' in names
    assert 'github_code' not in names


def test_registry_with_github_auth_includes_github_scanners():
    scanners = build_scanners(_config('token'))
    names = {scanner.name for scanner in scanners}
    assert 'github_code' in names
    assert 'github_releases' in names
    assert 'github_forks' in names
