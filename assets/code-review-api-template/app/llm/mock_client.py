from app.llm.base import LLMClient
from app.schemas.review import ReviewRequest, RiskItem


class MockLLMClient(LLMClient):
    def __init__(self, response: str | Exception):
        self.response = response

    def analyze_code(self, request: ReviewRequest, rule_findings: list[RiskItem]) -> str:
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    def repair_json(self, invalid_response: str, error: str) -> str:
        if isinstance(self.response, Exception):
            raise self.response
        return self.response
