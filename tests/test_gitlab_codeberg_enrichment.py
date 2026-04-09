from app_crawler.scanners.gitlab import GitLabScanner
from app_crawler.scanners.codeberg import CodebergScanner
from app_crawler.models import ReleaseInfo


def test_gitlab_enrichment_without_project_id_returns_base_urls():
    scanner = GitLabScanner()
    info, desc, urls = scanner._enrich_project({
        'description': 'demo',
        'web_url': 'https://gitlab.com/example/demo',
        'homepage': 'https://example.com',
    })
    assert isinstance(info, ReleaseInfo)
    assert 'https://gitlab.com/example/demo' in urls
    assert 'https://example.com' in urls
    assert desc == 'demo'


def test_codeberg_enrichment_without_full_name_returns_base_urls():
    scanner = CodebergScanner()
    info, desc, urls = scanner._enrich_repo({
        'description': 'demo',
        'html_url': 'https://codeberg.org/example/demo',
        'website': 'https://example.com',
    })
    assert isinstance(info, ReleaseInfo)
    assert 'https://codeberg.org/example/demo' in urls
    assert 'https://example.com' in urls
    assert desc == 'demo'
