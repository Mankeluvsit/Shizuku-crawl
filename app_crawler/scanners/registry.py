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
    preset = config.preset
    all_factories: dict[str, ScannerFactory] = {
        'fdroid_primary': _fdroid_primary,
        'fdroid_izzy': _fdroid_izzy,
        'gitlab': _gitlab,
        'codeberg': _codeberg,
        'github_code': _github_code,
        'github_meta': _github_meta,
        'github_releases': _github_releases,
        'github_forks': _github_forks,
    }

    if preset == 'fdroid-only':
        names = ['fdroid_primary', 'fdroid_izzy']
    elif preset == 'github-only':
        names = ['github_code', 'github_meta', 'github_releases', 'github_forks']
    elif preset == 'non-github':
        names = ['fdroid_primary', 'fdroid_izzy', 'gitlab', 'codeberg']
    elif preset == 'quick':
        names = ['fdroid_primary', 'github_meta', 'gitlab']
    else:
        names = list(all_factories.keys())

    factories = [all_factories[name] for name in names if name in all_factories]
    if preset in {'github-only', 'full', 'quick'} and not config.github_auth:
        factories = [factory for factory in factories if factory not in {_github_code, _github_meta, _github_releases, _github_forks}]
    return factories


def build_scanners(config: AppConfig) -> list[BaseScanner]:
    return [factory(config) for factory in get_scanner_factories(config)]
