from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


class MetricsSession(requests.Session):
    def __init__(self) -> None:
        super().__init__()
        self.metrics = {
            'request_count': 0,
            'retry_count': 0,
            'rate_limit_hits': 0,
            'failed_requests': 0,
        }

    def request(self, method, url, *args, **kwargs):
        self.metrics['request_count'] += 1
        try:
            response = super().request(method, url, *args, **kwargs)
        except Exception:
            self.metrics['failed_requests'] += 1
            raise

        history = getattr(getattr(response, 'raw', None), 'retries', None)
        retry_history = getattr(history, 'history', ()) or ()
        self.metrics['retry_count'] += len(retry_history)

        status_codes = []
        for item in retry_history:
            status = getattr(item, 'status', None)
            if status is not None:
                status_codes.append(status)
        status_codes.append(response.status_code)

        self.metrics['rate_limit_hits'] += sum(1 for code in status_codes if code == 429)
        if response.status_code >= 400:
            self.metrics['failed_requests'] += 1
        return response


def build_retry_session(
    total_retries: int = 3,
    backoff_factor: float = 0.75,
    status_forcelist: tuple[int, ...] = DEFAULT_RETRY_STATUS_CODES,
) -> MetricsSession:
    session = MetricsSession()
    retry = Retry(
        total=total_retries,
        connect=total_retries,
        read=total_retries,
        status=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET", "HEAD", "OPTIONS"]),
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_session_metrics(session: requests.Session | None) -> dict[str, int]:
    if session is None:
        return {
            'request_count': 0,
            'retry_count': 0,
            'rate_limit_hits': 0,
            'failed_requests': 0,
        }
    metrics = getattr(session, 'metrics', None)
    if not isinstance(metrics, dict):
        return {
            'request_count': 0,
            'retry_count': 0,
            'rate_limit_hits': 0,
            'failed_requests': 0,
        }
    return {
        'request_count': int(metrics.get('request_count', 0) or 0),
        'retry_count': int(metrics.get('retry_count', 0) or 0),
        'rate_limit_hits': int(metrics.get('rate_limit_hits', 0) or 0),
        'failed_requests': int(metrics.get('failed_requests', 0) or 0),
    }
