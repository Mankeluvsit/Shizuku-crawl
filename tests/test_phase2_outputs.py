from pathlib import Path

from app_crawler.models import AppResult, MatchEvidence, ReleaseInfo
from app_crawler.outputs import write_html, write_stats


def test_html_contains_filters(tmp_path: Path):
    app = AppResult(
        name="Demo",
        urls=["https://example.com"],
        scanner="github_releases",
        confidence="high",
        usefulness="high",
        evidence=[MatchEvidence(source="x", reason="github-release-scan", detail="owner/repo")],
        release_info=ReleaseInfo(has_downloads=True, release_url="https://example.com/release", release_tag="v1", apk_assets=["app.apk"]),
    )
    out = tmp_path / "apps.html"
    write_html(out, [app])
    text = out.read_text(encoding="utf-8")
    assert "Search and filter results" in text
    assert "github_releases" in text
    assert "app.apk" in text


def test_stats_include_scanner_counts(tmp_path: Path):
    apps = [
        AppResult(name="A", urls=["https://a"], scanner="github_releases"),
        AppResult(name="B", urls=["https://b"], scanner="github_forks"),
    ]
    out = tmp_path / "scan_stats.json"
    write_stats(out, apps)
    text = out.read_text(encoding="utf-8")
    assert "github_releases" in text
    assert "github_forks" in text
