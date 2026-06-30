from collections.abc import Generator

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.repository import ReviewRepository
from app.llm.base import LLMClient
from app.llm.qwen_client import QwenClient
from app.services.review_service import ReviewService


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_llm_client() -> LLMClient:
    return QwenClient(
        api_key=settings.qwen_api_key,
        base_url=settings.qwen_base_url,
        model=settings.qwen_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )


def get_review_service() -> Generator[ReviewService, None, None]:
    db = SessionLocal()
    try:
        yield ReviewService(repository=ReviewRepository(db), llm_client=get_llm_client())
    finally:
        db.close()
