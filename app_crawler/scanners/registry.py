from __future__ import annotations

from typing import Callable

from ..config import AppConfig
from .base import BaseScanner
from .fdroid import FDroidScanner
from .gitlab import GitLabScanner
from .codeberg import CodebergScanner
from .github_code import GithubCodeScanner
from .github_meta import GithubMetaScanner
from .github_releases import GithubReleasesScanner
from .github_forks import GithubForksScanner

ScannerFactory = Callable[[AppConfig], BaseScanner]


def _fdroid_primary(_: AppConfig) -> BaseScanner:
    return FDroidScanner("https://f-droid.org/repo/index.xml")


def _fdroid_izzy(_: AppConfig) -> BaseScanner:
    return FDroidScanner("https://apt.izzysoft.de/fdroid/repo/index.xml")


def _gitlab(_: AppConfig) -> BaseScanner:
    return GitLabScanner()


def _codeberg(_: AppConfig) -> BaseScanner:
    return CodebergScanner()


def _github_code(config: AppConfig) -> BaseScanner:
    return GithubCodeScanner(config.github_auth or "", process_count=config.process_count)


def _github_meta(config: AppConfig) -> BaseScanner:
    return GithubMetaScanner(config.github_auth or "", process_count=config.process_count)


def _github_releases(config: AppConfig) -> BaseScanner:
    return GithubReleasesScanner(config.github_auth or "", process_count=config.process_count)


def _github_forks(config: AppConfig) -> BaseScanner:
    return GithubForksScanner(config.github_auth or "", process_count=config.process_count)


def get_scanner_factories(config: AppConfig) -> list[ScannerFactory]:
    factories: list[ScannerFactory] = [
        _fdroid_primary,
        _fdroid_izzy,
        _gitlab,
        _codeberg,
    ]
    if config.github_auth:
        factories.extend([
            _github_code,
            _github_meta,
            _github_releases,
            _github_forks,
        ])
    return factories


def build_scanners(config: AppConfig) -> list[BaseScanner]:
    return [factory(config) for factory in get_scanner_factories(config)]
