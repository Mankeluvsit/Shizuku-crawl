from __future__ import annotations

from collections.abc import Iterable

STRICT_GITHUB_CODE_QUERIES = [
    '"rikka.shizuku" language:Java',
    '"rikka.shizuku" language:Kotlin',
    '"moe.shizuku" language:Java',
    '"moe.shizuku" language:Kotlin',
    '"ShizukuProvider" language:Java',
    '"ShizukuProvider" language:Kotlin',
    '"ShizukuBinderWrapper" language:Java',
    '"ShizukuBinderWrapper" language:Kotlin',
]

BROAD_GITHUB_CODE_EXTRA_QUERIES = [
    '"Shizuku.pingBinder" language:Java',
    '"Shizuku.pingBinder" language:Kotlin',
    '"Shizuku.getUid" language:Java',
    '"Shizuku.getUid" language:Kotlin',
    '"addRequestPermissionResultListener" language:Java Shizuku',
    '"addRequestPermissionResultListener" language:Kotlin Shizuku',
    '"Shizuku" language:Java',
    '"Shizuku" language:Kotlin',
]

STRICT_GITHUB_REPO_QUERIES = [
    '"rikka.shizuku" in:readme',
    '"moe.shizuku" in:readme',
    '"requires shizuku" in:readme',
    '"uses shizuku" in:readme',
    '"powered by shizuku" in:readme',
]

BROAD_GITHUB_REPO_EXTRA_QUERIES = [
    'shizuku in:readme',
    'shizuku in:name,description',
]


def expand_queries(mode: str, strict_queries: Iterable[str], broad_extra_queries: Iterable[str]) -> list[str]:
    queries = list(strict_queries)
    if mode == 'broad':
        queries.extend(broad_extra_queries)
    seen: set[str] = set()
    out: list[str] = []
    for query in queries:
        if query not in seen:
            seen.add(query)
            out.append(query)
    return out


def paginated_search_items(session, url: str, *, query: str, per_page: int, pages: int, timeout: int = 30) -> list[dict]:
    items: list[dict] = []
    for page in range(1, max(1, pages) + 1):
        response = session.get(
            url,
            params={"q": query, "per_page": per_page, "page": page},
            timeout=timeout,
        )
        response.raise_for_status()
        page_items = response.json().get("items", [])
        if not page_items:
            break
        items.extend(page_items)
        if len(page_items) < per_page:
            break
    return items


def classify_github_code_query(query: str) -> str:
    lowered = query.lower()
    strong_markers = ['rikka.shizuku', 'moe.shizuku', 'shizukuprovider', 'shizukubinderwrapper']
    if any(marker in lowered for marker in strong_markers):
        return 'strong'
    medium_markers = ['shizuku.pingbinder', 'shizuku.getuid', 'addrequestpermissionresultlistener']
    if any(marker in lowered for marker in medium_markers):
        return 'medium'
    return 'medium' if 'shizuku' in lowered else 'weak'


def classify_github_repo_query(query: str) -> str:
    lowered = query.lower()
    medium_markers = ['rikka.shizuku', 'moe.shizuku', 'requires shizuku', 'uses shizuku', 'powered by shizuku']
    if any(marker in lowered for marker in medium_markers):
        return 'medium'
    return 'weak'
