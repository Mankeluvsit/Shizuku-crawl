from app_crawler.models import AppResult, ReviewState


def test_identity_merge_prefers_package_id():
    a = AppResult(name="One", urls=["https://a"], scanner="x", package_id="com.example.app")
    b = AppResult(name="Two", urls=["https://b"], scanner="y", package_id="com.example.app")
    merged = a.merge(b)
    assert merged.package_id == "com.example.app"
    assert len(merged.urls) == 2


def test_review_state_applies():
    app = AppResult(name="One", urls=["https://a"], scanner="x")
    state = ReviewState(status="confirmed", review_notes="looks good", reviewed_by="adam")
    app.apply_review_state(state)
    assert app.status == "confirmed"
    assert app.review_notes == "looks good"
    assert app.reviewed_by == "adam"
