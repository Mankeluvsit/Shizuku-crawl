from __future__ import annotations

from .models import ReleaseInfo


def classify_release_assets(asset_names: list[str], release_url: str | None = None, release_tag: str | None = None, release_published_at: str | None = None) -> ReleaseInfo:
    lowered = [name.lower() for name in asset_names]
    apk_assets = [name for name in asset_names if name.lower().endswith('.apk')]
    aab_assets = [name for name in asset_names if name.lower().endswith('.aab')]
    universal_apk_assets = [name for name in apk_assets if 'universal' in name.lower()]
    split_apk_assets = [name for name in apk_assets if any(token in name.lower() for token in ['arm64', 'armeabi', 'x86', 'x86_64', 'split', 'config.', 'dpi']) and name not in universal_apk_assets]
    checksum_assets = [name for name in asset_names if name.lower().endswith(('.sha256', '.sha512', '.sha1', '.md5', '.sig', '.asc', '.minisig', '.txt')) and any(token in name.lower() for token in ['sha', 'md5', 'sig', 'asc', 'minisig', 'checksum'])]

    quality_label = 'none'
    if universal_apk_assets and checksum_assets:
        quality_label = 'strong'
    elif apk_assets or aab_assets:
        quality_label = 'installable'
    elif asset_names:
        quality_label = 'assets_only'

    return ReleaseInfo(
        has_downloads=bool(asset_names),
        release_url=release_url,
        release_tag=release_tag,
        release_published_at=release_published_at,
        apk_assets=apk_assets,
        aab_assets=aab_assets,
        universal_apk_assets=universal_apk_assets,
        split_apk_assets=split_apk_assets,
        checksum_assets=checksum_assets,
        quality_label=quality_label,
    )
