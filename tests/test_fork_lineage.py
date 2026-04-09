from app_crawler.models import AppResult, ForkLineage
from app_crawler.outputs import write_csv
from pathlib import Path


def test_fork_lineage_serialization():
    lineage = ForkLineage(parent_full_name='owner/parent', ahead_by=5, behind_by=1, is_meaningfully_ahead=True)
    data = lineage.to_dict()
    restored = ForkLineage.from_dict(data)
    assert restored.parent_full_name == 'owner/parent'
    assert restored.ahead_by == 5
    assert restored.is_meaningfully_ahead is True


def test_csv_contains_fork_lineage(tmp_path: Path):
    app = AppResult(name='Fork', urls=['https://example.com'], scanner='github_forks', fork_lineage=ForkLineage(parent_full_name='owner/parent', ahead_by=4, behind_by=0, is_meaningfully_ahead=True))
    out = tmp_path / 'apps.csv'
    write_csv(out, [app])
    text = out.read_text(encoding='utf-8')
    assert 'owner/parent' in text
    assert 'fork_meaningfully_ahead' in text
