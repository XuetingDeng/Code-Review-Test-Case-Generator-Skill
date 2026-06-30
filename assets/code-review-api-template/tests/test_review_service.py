import json

from app.db.repository import ReviewRepository
from app.llm.mock_client import MockLLMClient
from app.schemas.review import ReviewRequest
from app.services.review_service import ReviewService


def test_service_saves_review(db_session, valid_llm_response):
    service = ReviewService(ReviewRepository(db_session), MockLLMClient(valid_llm_response))
    response = service.create_review(ReviewRequest(language="python", code="def ok():\n    return 1"))
    assert response.review_id == 1
    assert response.fallback_used is False


def test_service_fallback_on_invalid_json(db_session):
    service = ReviewService(ReviewRepository(db_session), MockLLMClient("not json"))
    response = service.create_review(ReviewRequest(language="python", code="def divide(a,b):\n    return a / b"))
    assert response.fallback_used is True
    assert response.review_result == "HIGH_RISK"


def test_service_accepts_markdown_json_after_parse(db_session):
    payload = {
        "summary": "ok",
        "risks": [],
        "test_cases": [{"name": "test_ok", "input": "x", "expected": "y", "reason": "coverage"}],
        "test_code": None,
        "review_result": "PASS",
    }
    service = ReviewService(ReviewRepository(db_session), MockLLMClient(f"```json\n{json.dumps(payload)}\n```"))
    response = service.create_review(ReviewRequest(language="python", code="def ok():\n    return 1"))
    assert response.review_result == "PASS"
