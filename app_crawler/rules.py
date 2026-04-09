from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .models import AppResult


@dataclass(slots=True)
class RuleSet:
    ignore_names: set[str] = field(default_factory=set)
    ignore_urls: set[str] = field(default_factory=set)
    include_names: set[str] = field(default_factory=set)
    include_urls: set[str] = field(default_factory=set)
    aliases: dict[str, str] = field(default_factory=dict)
    scoring_rules: dict[str, list[str]] = field(default_factory=dict)


DEFAULT_SCORING_RULES = {
    "confidence_high_markers": ["rikka.shizuku", "fdroid-metadata", "github-code-search"],
    "confidence_medium_markers": ["shizuku", "github-repository-search"],
    "usefulness_high_markers": ["has_downloads"],
}


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def load_rule_set(rules_dir: Path) -> RuleSet:
    ignore = _read_yaml(rules_dir / "ignore.yaml")
    include = _read_yaml(rules_dir / "include.yaml")
    aliases = _read_yaml(rules_dir / "aliases.yaml")
    scoring = _read_yaml(rules_dir / "rules.yaml")
    merged_scoring = {**DEFAULT_SCORING_RULES, **(scoring.get("scoring", {}) if isinstance(scoring, dict) else {})}
    alias_map = aliases.get("aliases", {}) if isinstance(aliases, dict) else {}
    return RuleSet(
        ignore_names=set(ignore.get("names", []) if isinstance(ignore, dict) else []),
        ignore_urls=set(ignore.get("urls", []) if isinstance(ignore, dict) else []),
        include_names=set(include.get("names", []) if isinstance(include, dict) else []),
        include_urls=set(include.get("urls", []) if isinstance(include, dict) else []),
        aliases={str(k): str(v) for k, v in alias_map.items()},
        scoring_rules={k: list(v) for k, v in merged_scoring.items()},
    )


def should_ignore(app: AppResult, rules: RuleSet) -> bool:
    return app.name in rules.ignore_names or any(url in rules.ignore_urls for url in app.urls)


def should_force_include(app: AppResult, rules: RuleSet) -> bool:
    return app.name in rules.include_names or any(url in rules.include_urls for url in app.urls)


def apply_aliases(apps: list[AppResult], aliases: dict[str, str]) -> list[AppResult]:
    for app in apps:
        if app.name in aliases:
            app.name = aliases[app.name]
    return apps
