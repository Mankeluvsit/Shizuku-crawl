from app_crawler.scanners.gitlab import GitLabScanner
from app_crawler.scanners.codeberg import CodebergScanner


def test_gitlab_scanner_metadata():
    scanner = GitLabScanner()
    assert scanner.name == "gitlab"
    assert scanner.source_type == "gitlab_project"


def test_codeberg_scanner_metadata():
    scanner = CodebergScanner()
    assert scanner.name == "codeberg"
    assert scanner.source_type == "codeberg_repo"
