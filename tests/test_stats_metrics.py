from pathlib import Path

from app_crawler.models import AppResult
from app_crawler.outputs import write_stats


def test_write_stats_includes_scanner_metrics(tmp_path: Path):
    apps = [AppResult(name='A', urls=['https://a'], scanner='github_releases')]
    out = tmp_path / 'scan_stats.json'
    write_stats(out, apps, scanner_metrics={
        'github_releases': {
            'items_found': 3,
            'elapsed_ms': 125.5,
            'ok': True,
            'error': None,
        }
    })
    text = out.read_text(encoding='utf-8')
    assert 'scanner_metrics' in text
    assert 'elapsed_ms' in text
    assert 'github_releases' in text
