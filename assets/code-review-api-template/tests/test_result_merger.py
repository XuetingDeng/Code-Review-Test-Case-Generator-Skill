from app.schemas.review import ReviewResult, RiskItem, TestCaseItem
from app.services.result_merger import ResultMerger


def result_with(risks):
    return ReviewResult(
        summary="summary",
        risks=risks,
        test_cases=[TestCaseItem(name="test_ok", input="x", expected="y", reason="coverage")],
        test_code=None,
        review_result="PASS",
    )


def test_high_risk_from_rules_wins():
    risk = RiskItem(type="SECURITY", level="HIGH", description="eval", suggestion="avoid")
    merged = ResultMerger().merge([risk], result_with([]))
    assert merged.review_result == "HIGH_RISK"


def test_medium_risk_needs_changes():
    risk = RiskItem(type="MAINTAINABILITY", level="MEDIUM", description="open", suggestion="with")
    merged = ResultMerger().merge([risk], result_with([]))
    assert merged.review_result == "NEEDS_CHANGES"


def test_clean_result_passes():
    merged = ResultMerger().merge([], result_with([]))
    assert merged.review_result == "PASS"
