import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ReviewRecord
from app.schemas.review import ReviewRequest, ReviewResponse, ReviewResult


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        request: ReviewRequest,
        result: ReviewResult,
        raw_llm_response: str | None,
        fallback_used: bool,
        error_message: str | None = None,
    ) -> ReviewRecord:
        record = ReviewRecord(
            language=request.language,
            review_type=request.review_type,
            code=request.code,
            focus=json.dumps(request.focus),
            summary=result.summary,
            risks=json.dumps([item.model_dump() for item in result.risks]),
            test_cases=json.dumps([item.model_dump() for item in result.test_cases]),
            test_code=result.test_code,
            review_result=result.review_result,
            fallback_used=fallback_used,
            llm_raw_response=raw_llm_response,
            error_message=error_message,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list(self, limit: int, language: str | None, review_result: str | None) -> list[ReviewRecord]:
        query = select(ReviewRecord).order_by(ReviewRecord.created_at.desc()).limit(limit)
        if language:
            query = query.where(ReviewRecord.language == language)
        if review_result:
            query = query.where(ReviewRecord.review_result == review_result)
        return list(self.db.scalars(query))

    def get(self, review_id: int) -> ReviewRecord | None:
        return self.db.get(ReviewRecord, review_id)


def record_to_response(record: ReviewRecord) -> ReviewResponse:
    return ReviewResponse(
        review_id=record.id,
        summary=record.summary,
        risks=json.loads(record.risks),
        test_cases=json.loads(record.test_cases),
        test_code=record.test_code,
        review_result=record.review_result,
        fallback_used=record.fallback_used,
        created_at=record.created_at,
    )
