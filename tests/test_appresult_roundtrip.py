from app_crawler.models import AppResult, ForkLineage, ReleaseInfo


def test_appresult_roundtrip_with_release_and_fork_fields():
    app = AppResult(
        name='Demo',
        urls=['https://example.com'],
        scanner='github_forks',
        release_info=ReleaseInfo(quality_label='installable', apk_assets=['app.apk']),
        fork_lineage=ForkLineage(parent_full_name='owner/parent', ahead_by=4, behind_by=1, is_meaningfully_ahead=True),
    )
    restored = AppResult.from_dict(app.to_dict())
    assert restored.release_info.quality_label == 'installable'
    assert restored.fork_lineage.parent_full_name == 'owner/parent'
    assert restored.fork_lineage.is_meaningfully_ahead is True
