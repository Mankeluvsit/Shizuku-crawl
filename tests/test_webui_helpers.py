from pathlib import Path

from app_crawler.cache import Cache
from app_crawler.models import AppResult
from app_crawler.webui import HTML, _load_apps_for_ui, _save_review_update


def test_save_review_update_persists_review_state(tmp_path: Path):
    cache = Cache(tmp_path / 'cache')
    _save_review_update(cache, 'name::https://example.com', 'confirmed', 'looks good', 'adam')
    state = cache.load_review_state()
    assert state['name::https://example.com'].status == 'confirmed'
    assert state['name::https://example.com'].review_notes == 'looks good'
    assert state['name::https://example.com'].reviewed_by == 'adam'


def test_load_apps_for_ui_applies_saved_review_state(tmp_path: Path):
    cache = Cache(tmp_path / 'cache')
    app = AppResult(name='Demo', urls=['https://example.com'], scanner='gitlab')
    cache.save_current_run([app])
    _save_review_update(cache, app.identity_key_str(), 'reviewed', 'done', 'adam')
    apps = _load_apps_for_ui(cache)
    assert apps[0]['status'] == 'reviewed'
    assert apps[0]['review_notes'] == 'done'
    assert apps[0]['reviewed_by'] == 'adam'
    assert apps[0]['identity_key'] == app.identity_key_str()


def test_webui_contains_quick_review_action_buttons():
    assert 'Mark confirmed' in HTML
    assert 'Mark reviewed' in HTML
    assert 'Mark false_positive' in HTML
    assert 'Mark archived' in HTML


def test_webui_contains_mobile_friendly_layout_markers():
    assert 'viewport' in HTML
    assert '@media (max-width: 900px)' in HTML
    assert 'scrollIntoView' in HTML
    assert 'button-row' in HTML


def test_webui_contains_translate_markers():
    assert 'Translate description' in HTML
    assert 'Original language:' in HTML
    assert 'translate.google.com' in HTML
