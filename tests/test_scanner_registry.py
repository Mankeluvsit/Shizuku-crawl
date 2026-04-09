from app_crawler.config import AppConfig
from app_crawler.scanners.registry import build_scanners, get_scanner_factories
from pathlib import Path


def _config(github_auth: str | None, preset: str = 'full'):
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
        preset=preset,
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


def test_registry_factory_count_changes_with_auth():
    without_auth = get_scanner_factories(_config(None))
    with_auth = get_scanner_factories(_config('token'))
    assert len(without_auth) < len(with_auth)


def test_fdroid_only_preset_only_builds_fdroid_scanners():
    scanners = build_scanners(_config(None, preset='fdroid-only'))
    names = [scanner.name for scanner in scanners]
    assert names == ['fdroid', 'fdroid']


def test_github_only_preset_without_auth_builds_no_scanners():
    scanners = build_scanners(_config(None, preset='github-only'))
    assert scanners == []


def test_non_github_preset_excludes_github_scanners():
    scanners = build_scanners(_config('token', preset='non-github'))
    names = {scanner.name for scanner in scanners}
    assert 'github_code' not in names
    assert 'gitlab' in names
    assert 'codeberg' in names


def test_quick_preset_builds_small_subset():
    scanners = build_scanners(_config('token', preset='quick'))
    names = [scanner.name for scanner in scanners]
    assert names == ['fdroid', 'github_meta', 'gitlab']
