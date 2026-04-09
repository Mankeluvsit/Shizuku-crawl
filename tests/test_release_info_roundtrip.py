from app_crawler.models import ReleaseInfo


def test_release_info_roundtrip_with_quality_fields():
    original = ReleaseInfo(
        has_downloads=True,
        release_url='https://example.com/release',
        release_tag='v1',
        release_published_at='2026-01-01T00:00:00Z',
        apk_assets=['app.apk'],
        aab_assets=['app.aab'],
        universal_apk_assets=['app-universal.apk'],
        split_apk_assets=['app-arm64.apk'],
        checksum_assets=['checksums.sha256'],
        quality_label='strong',
    )
    restored = ReleaseInfo.from_dict(original.to_dict())
    assert restored.quality_label == 'strong'
    assert restored.universal_apk_assets == ['app-universal.apk']
    assert restored.checksum_assets == ['checksums.sha256']
