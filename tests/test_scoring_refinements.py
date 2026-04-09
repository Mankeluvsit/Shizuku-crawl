from app_crawler.models import AppResult, ForkLineage, MatchEvidence, ReleaseInfo
from app_crawler.scoring import score_apps


def _rules():
    return {
        'confidence_high_markers': ['github-code-search'],
        'confidence_medium_markers': ['github-repository-search'],
    }


def test_strong_artifact_quality_scores_high_usefulness():
    app = AppResult(
        name='A',
        urls=['https://a'],
        scanner='github_releases',
        release_info=ReleaseInfo(quality_label='strong', checksum_assets=['checksums.sha256'], universal_apk_assets=['app-universal.apk']),
    )
    scored = score_apps([app], _rules())
    assert scored[0].usefulness == 'high'


def test_installable_and_meaningfully_ahead_scores_high_usefulness():
    app = AppResult(
        name='B',
        urls=['https://b'],
        scanner='github_forks',
        release_info=ReleaseInfo(quality_label='installable'),
        fork_lineage=ForkLineage(parent_full_name='owner/parent', ahead_by=4, behind_by=0, is_meaningfully_ahead=True),
    )
    scored = score_apps([app], _rules())
    assert scored[0].usefulness == 'high'


def test_release_hint_without_installable_assets_scores_medium_or_low():
    app = AppResult(
        name='C',
        urls=['https://c'],
        scanner='gitlab',
        has_downloads=True,
        release_info=ReleaseInfo(release_tag='v1', release_url='https://example.com/release', quality_label='assets_only'),
    )
    scored = score_apps([app], _rules())
    assert scored[0].usefulness == 'medium'


def test_confidence_markers_still_apply():
    app = AppResult(
        name='D',
        urls=['https://d'],
        scanner='github_code',
        evidence=[MatchEvidence(source='x', reason='github-code-search')],
    )
    scored = score_apps([app], _rules())
    assert scored[0].confidence == 'high'
