from __future__ import annotations

from pathlib import Path

from .models import AppResult


def load_reference_paths(target_path: Path) -> list[Path]:
    readmes = sorted(p for p in target_path.glob("*.md") if p.is_file())
    unlisted = target_path / "pages" / "UNLISTED.md"
    if unlisted.exists():
        readmes.append(unlisted)
    return readmes


def load_reference_text(target_path: Path) -> str:
    chunks: list[str] = []
    for path in load_reference_paths(target_path):
        try:
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
    return "\n".join(chunks)


def filter_known_apps(apps: list[AppResult], target_path: Path) -> list[AppResult]:
    corpus = load_reference_text(target_path)
    if not corpus:
        return apps

    filtered: list[AppResult] = []
    for app in apps:
        if app.name and app.name in corpus:
            continue
        if any(url in corpus for url in app.urls):
            continue
        filtered.append(app)
    return filtered
