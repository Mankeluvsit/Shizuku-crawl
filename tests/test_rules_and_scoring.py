from app_crawler.models import AppResult, MatchEvidence
from app_crawler.rules import RuleSet, should_force_include, should_ignore
from app_crawler.scoring import score_apps


def test_rules_ignore_and_include():
    rules = RuleSet(ignore_names={"BadApp"}, include_names={"GoodApp"})
    bad = AppResult(name="BadApp", urls=["https://a"], scanner="x")
    good = AppResult(name="GoodApp", urls=["https://b"], scanner="x")
    assert should_ignore(bad, rules) is True
    assert should_force_include(good, rules) is True


def test_scoring_from_rules():
    app = AppResult(name="A", urls=["https://a"], scanner="x", evidence=[MatchEvidence(source="x", reason="github-code-search")])
    scored = score_apps([app], {"confidence_high_markers": ["github-code-search"], "confidence_medium_markers": []})
    assert scored[0].confidence == "high"
