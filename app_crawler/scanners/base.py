from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import AppResult


class BaseScanner(ABC):
    name = "base"
    source_type = "unknown"
    trust_level = "medium"

    @abstractmethod
    def find_matching_apps(self) -> list[AppResult]:
        raise NotImplementedError
