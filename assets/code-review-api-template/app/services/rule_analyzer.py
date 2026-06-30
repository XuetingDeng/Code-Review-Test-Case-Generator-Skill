import re

from app.schemas.review import ReviewRequest, RiskItem


class RuleAnalyzer:
    def analyze(self, request: ReviewRequest) -> list[RiskItem]:
        if request.language == "python":
            return self._analyze_python(request.code)
        if request.language == "java":
            return self._analyze_java(request.code)
        return []

    def _analyze_python(self, code: str) -> list[RiskItem]:
        risks: list[RiskItem] = []
        lowered = code.lower()

        if re.search(r"except\s*:", code):
            risks.append(self._risk("EXCEPTION", "HIGH", "Bare except block catches all exceptions.", "Catch specific exception types and handle them explicitly."))
        if re.search(r"except\s+Exception\b", code) and not re.search(r"(logging\.|logger\.|raise\b)", code):
            risks.append(self._risk("EXCEPTION", "MEDIUM", "Broad exception handler does not log or re-raise.", "Log the exception or re-raise after adding context."))
        if "/" in code and not re.search(r"!=\s*0|==\s*0|if\s+.*\bzero\b", lowered):
            risks.append(self._risk("EXCEPTION", "HIGH", "Division is used without an obvious zero check.", "Validate denominators before division."))
        if re.search(r"\w+\s*\[[^\]]+\]", code) and not re.search(r"len\s*\(|in\s+\w+|\.get\s*\(", code):
            risks.append(self._risk("EDGE_CASE", "MEDIUM", "Index or key access appears unchecked.", "Check bounds or key existence before direct access."))
        if re.search(r"\bopen\s*\(", code) and "with open" not in code:
            risks.append(self._risk("MAINTAINABILITY", "MEDIUM", "File is opened without a context manager.", "Use `with open(...)` so the file is closed reliably."))
        if re.search(r"\b(eval|exec)\s*\(", code):
            risks.append(self._risk("SECURITY", "HIGH", "Dynamic code execution detected.", "Avoid eval/exec or strictly sandbox and validate input."))
        if re.search(r"(select|insert|update|delete).*(\+|%|\bf\")", lowered, re.DOTALL):
            risks.append(self._risk("SECURITY", "HIGH", "Possible SQL string construction from dynamic values.", "Use parameterized SQL queries."))
        return risks

    def _analyze_java(self, code: str) -> list[RiskItem]:
        risks: list[RiskItem] = []
        lowered = code.lower()
        if "/" in code and not re.search(r"!=\s*0|==\s*0", code):
            risks.append(self._risk("EXCEPTION", "HIGH", "Division is used without an obvious zero check.", "Validate denominators before division."))
        if ".get()" in code and "isPresent()" not in code and "orElse" not in code:
            risks.append(self._risk("BUG", "MEDIUM", "Optional.get() appears without presence handling.", "Use isPresent, ifPresent, or orElse variants."))
        if re.search(r"\.get\s*\([^)]*\)", code) and not re.search(r"\.size\s*\(|bounds|index", lowered):
            risks.append(self._risk("EDGE_CASE", "MEDIUM", "List access appears to lack bounds checking.", "Validate indexes before calling get(index)."))
        if re.search(r"catch\s*\(\s*Exception\s+\w+\s*\)\s*\{\s*\}", code, re.DOTALL):
            risks.append(self._risk("EXCEPTION", "MEDIUM", "Exception is caught and ignored.", "Handle, log, or rethrow the exception."))
        if re.search(r"(select|insert|update|delete).*\+", lowered, re.DOTALL):
            risks.append(self._risk("SECURITY", "HIGH", "Possible SQL string concatenation.", "Use prepared statements with bound parameters."))
        if re.search(r"public\s+\w+[<>\w\s,]*\s+\w+\s*\([^)]*\)", code) and not re.search(r"null|Objects\.requireNonNull|@NotNull|if\s*\(", code):
            risks.append(self._risk("BUG", "LOW", "Public method inputs do not show validation.", "Validate required inputs before use."))
        return risks

    def _risk(self, risk_type: str, level: str, description: str, suggestion: str) -> RiskItem:
        return RiskItem(type=risk_type, level=level, description=description, suggestion=suggestion)
