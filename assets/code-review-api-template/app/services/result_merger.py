from app.schemas.review import ReviewResult, RiskItem


class ResultMerger:
    def merge(self, rule_findings: list[RiskItem], llm_result: ReviewResult) -> ReviewResult:
        risks = self._dedupe([*rule_findings, *llm_result.risks])
        result = llm_result.model_copy(update={"risks": risks})
        return result.model_copy(update={"review_result": self._classify(result)})

    def _dedupe(self, risks: list[RiskItem]) -> list[RiskItem]:
        seen: set[tuple[str, str]] = set()
        merged: list[RiskItem] = []
        for risk in risks:
            key = (risk.type, risk.description.lower().strip())
            if key not in seen:
                seen.add(key)
                merged.append(risk)
        return merged

    def _classify(self, result: ReviewResult) -> str:
        if result.review_result == "HIGH_RISK":
            return "HIGH_RISK"
        if any(r.level == "HIGH" and r.type in {"SECURITY", "BUG", "EXCEPTION"} for r in result.risks):
            return "HIGH_RISK"
        if any(r.level in {"MEDIUM", "HIGH"} for r in result.risks):
            return "NEEDS_CHANGES"
        if not result.test_cases:
            return "NEEDS_CHANGES"
        return "PASS"
