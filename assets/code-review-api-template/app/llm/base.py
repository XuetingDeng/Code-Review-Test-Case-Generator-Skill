from abc import ABC, abstractmethod

from app.schemas.review import ReviewRequest, RiskItem


class LLMClient(ABC):
    @abstractmethod
    def analyze_code(self, request: ReviewRequest, rule_findings: list[RiskItem]) -> str:
        raise NotImplementedError

    def repair_json(self, invalid_response: str, error: str) -> str:
        raise NotImplementedError("This client does not support repair prompts.")
