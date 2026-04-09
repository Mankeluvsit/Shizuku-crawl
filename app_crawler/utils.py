from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse


PACKAGE_RE = re.compile(r"\b(?:applicationId|package)\s*[=:]\s*[\"']([A-Za-z0-9_.]+)[\"']")


def normalize_url(url: str) -> str:
    if not url:
        return url
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    return urlunparse((scheme, netloc, path, "", "", ""))


def extract_package_id(text: str | None) -> str | None:
    if not text:
        return None
    match = PACKAGE_RE.search(text)
    if not match:
        return None
    return match.group(1)
