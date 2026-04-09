from app_crawler.scanners.discovery import (
    BROAD_GITHUB_CODE_EXTRA_QUERIES,
    BROAD_GITHUB_REPO_EXTRA_QUERIES,
    STRICT_GITHUB_CODE_QUERIES,
    STRICT_GITHUB_REPO_QUERIES,
    classify_github_code_query,
    classify_github_repo_query,
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
    assert 'shizuku in:name,description' in broad


def test_query_strength_classification():
    assert classify_github_code_query('"rikka.shizuku" language:Kotlin') == 'strong'
    assert classify_github_code_query('"Shizuku" language:Kotlin') == 'medium'
    assert classify_github_repo_query('"requires shizuku" in:readme') == 'medium'
    assert classify_github_repo_query('shizuku in:name,description') == 'weak'
