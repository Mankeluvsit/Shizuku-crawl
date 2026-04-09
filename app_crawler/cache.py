from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

from .models import AppResult, ReviewState


class Cache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.current_run_path = self.cache_dir / "current_run.json"
        self.review_state_path = self.cache_dir / "review_state.json"
        self.legacy_pickle_path = self.cache_dir / "apps.cache"

    def load_all(self) -> list[AppResult]:
        if self.current_run_path.exists():
            try:
                data = json.loads(self.current_run_path.read_text(encoding="utf-8"))
                return [AppResult.from_dict(item) for item in data]
            except Exception:
                pass

        if self.legacy_pickle_path.exists():
            try:
                with self.legacy_pickle_path.open("rb") as fh:
                    data: Any = pickle.load(fh)
                if isinstance(data, list):
                    return [item if isinstance(item, AppResult) else AppResult.from_dict(item) for item in data]
            except Exception:
                pass

        return []

    def save_current_run(self, apps: list[AppResult]) -> None:
        self.current_run_path.write_text(
            json.dumps([app.to_dict() for app in apps], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_review_state(self) -> dict[str, ReviewState]:
        if not self.review_state_path.exists():
            return {}
        try:
            data = json.loads(self.review_state_path.read_text(encoding="utf-8"))
            return {key: ReviewState.from_dict(value) for key, value in data.items()}
        except Exception:
            return {}

    def save_review_state(self, review_state: dict[str, ReviewState]) -> None:
        data = {key: value.to_dict() for key, value in review_state.items()}
        self.review_state_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
