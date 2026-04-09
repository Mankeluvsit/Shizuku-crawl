from app_crawler.release_assets import classify_release_assets


def test_classify_release_assets_strong_quality():
    info = classify_release_assets([
        'app-universal.apk',
        'checksums.sha256',
        'notes.txt',
    ], release_url='https://example.com', release_tag='v1')
    assert info.quality_label == 'strong'
    assert info.universal_apk_assets == ['app-universal.apk']
    assert 'checksums.sha256' in info.checksum_assets


def test_classify_release_assets_installable_split():
    info = classify_release_assets([
        'app-arm64-v8a.apk',
        'app-armeabi-v7a.apk',
    ])
    assert info.quality_label == 'installable'
    assert len(info.split_apk_assets) == 2


def test_classify_release_assets_assets_only():
    info = classify_release_assets(['source.zip'])
    assert info.quality_label == 'assets_only'
    assert not info.apk_assets
