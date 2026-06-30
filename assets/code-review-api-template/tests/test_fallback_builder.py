from app.schemas.review import ReviewRequest, RiskItem
from app.services.fallback_builder import FallbackBuilder


def test_fallback_with_high_rule_findings():
    request = ReviewRequest(language="python", code="eval(user_input)")
    risk = RiskItem(type="SECURITY", level="HIGH", description="eval", suggestion="avoid")
    result = FallbackBuilder().build(request, [risk], RuntimeError("boom"))
    assert result.review_result == "HIGH_RISK"
    assert result.risks == [risk]


def test_fallback_without_rule_findings():
    request = ReviewRequest(language="python", code="def ok():\n    return 1")
    result = FallbackBuilder().build(request, [], RuntimeError("boom"))
    assert result.review_result == "NEEDS_CHANGES"
    assert result.test_cases
