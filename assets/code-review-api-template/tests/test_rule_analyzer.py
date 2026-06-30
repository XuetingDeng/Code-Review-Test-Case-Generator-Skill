from app.schemas.review import ReviewRequest
from app.services.rule_analyzer import RuleAnalyzer


def test_python_division_by_zero_risk():
    request = ReviewRequest(language="python", code="def divide(a, b):\n    return a / b")
    risks = RuleAnalyzer().analyze(request)
    assert any(r.type == "EXCEPTION" and r.level == "HIGH" for r in risks)


def test_python_bare_except():
    request = ReviewRequest(language="python", code="try:\n    work()\nexcept:\n    pass")
    risks = RuleAnalyzer().analyze(request)
    assert any("Bare except" in r.description for r in risks)


def test_python_eval_security():
    request = ReviewRequest(language="python", code="def run(x):\n    return eval(x)")
    risks = RuleAnalyzer().analyze(request)
    assert any(r.type == "SECURITY" and r.level == "HIGH" for r in risks)


def test_java_optional_get_risk():
    request = ReviewRequest(language="java", code="return value.get();")
    risks = RuleAnalyzer().analyze(request)
    assert any("Optional.get" in r.description for r in risks)


def test_java_sql_concatenation_risk():
    request = ReviewRequest(language="java", code='String sql = "select * from users where id=" + id;')
    risks = RuleAnalyzer().analyze(request)
    assert any(r.type == "SECURITY" for r in risks)
