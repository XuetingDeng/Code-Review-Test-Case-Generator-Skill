import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_review_service
from app.db.database import Base
from app.db.repository import ReviewRepository
from app.llm.mock_client import MockLLMClient
from app.main import app
from app.services.review_service import ReviewService


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def valid_llm_response() -> str:
    return json.dumps(
        {
            "summary": "The code divides two values.",
            "risks": [],
            "test_cases": [
                {
                    "name": "test_divide_normal_case",
                    "input": "a=10, b=2",
                    "expected": "5",
                    "reason": "Covers the normal path.",
                }
            ],
            "test_code": "def test_divide_normal_case():\n    assert divide(10, 2) == 5",
            "review_result": "PASS",
        }
    )


@pytest.fixture()
def client(db_session, valid_llm_response):
    def override_service():
        return ReviewService(ReviewRepository(db_session), MockLLMClient(valid_llm_response))

    app.dependency_overrides[get_review_service] = override_service
    yield TestClient(app)
    app.dependency_overrides.clear()
