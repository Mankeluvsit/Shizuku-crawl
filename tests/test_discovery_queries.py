from app_crawler.scanners.discovery import (
    BROAD_GITHUB_CODE_EXTRA_QUERIES,
    BROAD_GITHUB_REPO_EXTRA_QUERIES,
    STRICT_GITHUB_CODE_QUERIES,
    STRICT_GITHUB_REPO_QUERIES,
    expand_queries,
)


def test_broad_code_queries_extend_strict_queries():
    strict = expand_queries('strict', STRICT_GITHUB_CODE_QUERIES, BROAD_GITHUB_CODE_EXTRA_QUERIES)
    broad = expand_queries('broad', STRICT_GITHUB_CODE_QUERIES, BROAD_GITHUB_CODE_EXTRA_QUERIES)
    assert len(broad) > len(strict)
    assert all(query in broad for query in strict)
    assert '"Shizuku" language:Kotlin' in broad


def test_broad_repo_queries_extend_strict_queries():
    strict = expand_queries('strict', STRICT_GITHUB_REPO_QUERIES, BROAD_GITHUB_REPO_EXTRA_QUERIES)
    broad = expand_queries('broad', STRICT_GITHUB_REPO_QUERIES, BROAD_GITHUB_REPO_EXTRA_QUERIES)
    assert len(broad) > len(strict)
    assert all(query in broad for query in strict)
    assert '"requires shizuku" in:readme' in broad
