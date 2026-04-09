from app_crawler.models import AppResult
from app_crawler.normalize import normalize_app
from app_crawler.utils import extract_package_id, normalize_url


def test_normalize_url():
    assert normalize_url("HTTPS://GitHub.com/Example/App/") == "https://github.com/Example/App"


def test_extract_package_id():
    text = 'applicationId "com.example.app"'
    assert extract_package_id(text) == "com.example.app"


def test_normalize_app_trims_fields():
    app = AppResult(name=" Name ", urls=["https://example.com/"], scanner="x", desc=" hello   world ")
    app = normalize_app(app)
    assert app.name == "Name"
    assert app.desc == "hello world"
