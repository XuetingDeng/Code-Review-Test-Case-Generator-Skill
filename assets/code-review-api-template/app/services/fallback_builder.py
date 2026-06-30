from app.schemas.review import ReviewRequest, ReviewResult, RiskItem, TestCaseItem


class FallbackBuilder:
    def build(self, request: ReviewRequest, rule_findings: list[RiskItem], error: Exception | None = None) -> ReviewResult:
        high = any(item.level == "HIGH" and item.type in {"BUG", "EXCEPTION", "SECURITY"} for item in rule_findings)
        return ReviewResult(
            summary="LLM analysis failed. This fallback result is based on deterministic rule checks.",
            risks=rule_findings,
            test_cases=[
                TestCaseItem(
                    name="test_normal_case",
                    input="Provide representative valid input",
                    expected="Expected successful output",
                    reason="Basic happy path coverage",
                ),
                TestCaseItem(
                    name="test_edge_case_from_static_review",
                    input="Provide boundary, invalid, or exceptional input",
                    expected="Expected controlled behavior",
                    reason="Covers the most likely edge case from deterministic review",
                ),
            ],
            test_code=None,
            review_result="HIGH_RISK" if high else "NEEDS_CHANGES",
        )
