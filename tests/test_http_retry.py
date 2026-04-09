from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

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


def test_retry_session_recovers_from_transient_503():
    state = {'count': 0}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            state['count'] += 1
            if state['count'] == 1:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b'try again')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok')

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        session = build_retry_session(total_retries=2, backoff_factor=0)
        response = session.get(f'http://127.0.0.1:{server.server_port}/', timeout=5)
        assert response.status_code == 200
        assert response.text == 'ok'
        assert state['count'] == 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_retry_session_recovers_from_transient_429():
    state = {'count': 0}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            state['count'] += 1
            if state['count'] == 1:
                self.send_response(429)
                self.send_header('Retry-After', '0')
                self.end_headers()
                self.wfile.write(b'rate limited')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok')

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        session = build_retry_session(total_retries=2, backoff_factor=0)
        response = session.get(f'http://127.0.0.1:{server.server_port}/', timeout=5)
        assert response.status_code == 200
        assert response.text == 'ok'
        assert state['count'] == 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
