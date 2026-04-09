from app_crawler.models import AppResult
from app_crawler.pipeline import _filter_incremental


def test_filter_incremental_returns_new_or_changed_apps():
    old = AppResult(name="A", urls=["https://a"], scanner="x", confidence="low")
    same = AppResult(name="A", urls=["https://a"], scanner="x", confidence="low")
    changed = AppResult(name="B", urls=["https://b"], scanner="x", confidence="high")
    previous = [old, AppResult(name="B", urls=["https://b"], scanner="x", confidence="low")]
    current = [same, changed, AppResult(name="C", urls=["https://c"], scanner="x")]
    result = _filter_incremental(current, previous)
    assert [app.name for app in result] == ["B", "C"]
