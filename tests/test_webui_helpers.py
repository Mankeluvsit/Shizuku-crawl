from pathlib import Path
import json

from app_crawler.cache import Cache
from app_crawler.models import AppResult, MatchEvidence
from app_crawler.webui import HTML, _load_apps_for_ui, _load_stats_for_ui, _save_review_update


def test_save_review_update_persists_review_state(tmp_path: Path):
    cache = Cache(tmp_path / 'cache')
    _save_review_update(cache, 'name::https://example.com', 'confirmed', 'looks good', 'adam')
    state = cache.load_review_state()
    assert state['name::https://example.com'].status == 'confirmed'
    assert state['name::https://example.com'].review_notes == 'looks good'
    assert state['name::https://example.com'].reviewed_by == 'adam'


def test_load_apps_for_ui_applies_saved_review_state(tmp_path: Path):
    cache = Cache(tmp_path / 'cache')
    app = AppResult(name='Demo', urls=['https://example.com'], scanner='gitlab', evidence=[MatchEvidence(source='gitlab', reason='x', evidence_strength='medium')])
    cache.save_current_run([app])
    _save_review_update(cache, app.identity_key_str(), 'reviewed', 'done', 'adam')
    apps = _load_apps_for_ui(cache)
    assert apps[0]['status'] == 'reviewed'
    assert apps[0]['review_notes'] == 'done'
    assert apps[0]['reviewed_by'] == 'adam'
    assert apps[0]['identity_key'] == app.identity_key_str()
    assert apps[0]['strongest_evidence_strength'] == 'medium'


def test_load_stats_for_ui_reads_stats_json(tmp_path: Path):
    stats_path = tmp_path / 'scan_stats.json'
    stats_path.write_text(json.dumps({'total': 4, 'scanner_metrics': {'gitlab': {'elapsed_ms': 5}}}), encoding='utf-8')
    stats = _load_stats_for_ui(stats_path)
    assert stats['total'] == 4
    assert stats['scanner_metrics']['gitlab']['elapsed_ms'] == 5


def test_webui_contains_dashboard_markers():
    assert 'Shizuku Crawler Dashboard' in HTML
    assert '/api/stats' in HTML
    assert 'In-app preview' in HTML
    assert 'Translation workspace' in HTML
    assert 'strengthFilter' in HTML
