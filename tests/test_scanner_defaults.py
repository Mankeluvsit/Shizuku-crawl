from app_crawler.scanners.fdroid import FDroidScanner
from app_crawler.scanners.github_code import GithubCodeScanner
from app_crawler.scanners.github_meta import GithubMetaScanner
from app_crawler.scanners.github_releases import GithubReleasesScanner
from app_crawler.scanners.github_forks import GithubForksScanner
from app_crawler.scanners.gitlab import GitLabScanner
from app_crawler.scanners.codeberg import CodebergScanner


def test_scanner_identity_defaults():
    scanners = [
        FDroidScanner('https://example.com/index.xml'),
        GithubCodeScanner('token'),
        GithubMetaScanner('token'),
        GithubReleasesScanner('token'),
        GithubForksScanner('token'),
        GitLabScanner(),
        CodebergScanner(),
    ]
    for scanner in scanners:
        assert scanner.name
        assert scanner.source_type
        assert scanner.trust_level in {'high', 'medium', 'low'}


def test_scanner_unique_names():
    names = {
        FDroidScanner('https://example.com/index.xml').name,
        GithubCodeScanner('token').name,
        GithubMetaScanner('token').name,
        GithubReleasesScanner('token').name,
        GithubForksScanner('token').name,
        GitLabScanner().name,
        CodebergScanner().name,
    }
    assert len(names) == 7
