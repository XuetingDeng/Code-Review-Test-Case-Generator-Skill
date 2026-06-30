from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Language = Literal["python", "java", "javascript", "typescript", "go"]
ReviewType = Literal["code_snippet", "git_diff"]
FocusArea = Literal["bug", "edge_case", "exception", "maintainability", "security", "test"]
RiskType = Literal["BUG", "EDGE_CASE", "EXCEPTION", "MAINTAINABILITY", "SECURITY"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
ReviewStatus = Literal["PASS", "NEEDS_CHANGES", "HIGH_RISK"]


class ReviewRequest(BaseModel):
    language: Language
    code: str = Field(..., max_length=20_000)
    review_type: ReviewType = "code_snippet"
    focus: list[FocusArea] = ["bug", "edge_case", "exception", "test"]
    generate_test_code: bool = True

    @field_validator("code")
    @classmethod
    def code_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Code cannot be empty.")
        return value

    @field_validator("focus")
    @classmethod
    def focus_not_empty(cls, value: list[FocusArea]) -> list[FocusArea]:
        if not value:
            raise ValueError("Focus cannot be empty.")
        return value


class RiskItem(BaseModel):
    type: RiskType
    level: RiskLevel
    description: str
    suggestion: str


class TestCaseItem(BaseModel):
    name: str
    input: str
    expected: str
    reason: str


class ReviewResult(BaseModel):
    summary: str
    risks: list[RiskItem]
    test_cases: list[TestCaseItem]
    test_code: str | None = None
    review_result: ReviewStatus


class ReviewResponse(ReviewResult):
    review_id: int
    fallback_used: bool
    created_at: datetime
