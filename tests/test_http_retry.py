from requests.adapters import HTTPAdapter

from app_crawler.http import build_retry_session


def test_build_retry_session_mounts_http_adapter():
    session = build_retry_session()
    assert isinstance(session.adapters['https://'], HTTPAdapter)
    assert isinstance(session.adapters['http://'], HTTPAdapter)


def test_build_retry_session_retry_configuration():
    session = build_retry_session(total_retries=5, backoff_factor=1.25)
    retry = session.adapters['https://'].max_retries
    assert retry.total == 5
    assert retry.backoff_factor == 1.25
    assert 429 in retry.status_forcelist
    assert 503 in retry.status_forcelist
