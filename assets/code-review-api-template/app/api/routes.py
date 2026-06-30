from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_review_service
from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.review_service import ReviewService

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/v1/reviews", response_model=ReviewResponse)
def create_review(
    request: ReviewRequest,
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    try:
        return service.create_review(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/v1/reviews", response_model=list[ReviewResponse])
def list_reviews(
    limit: int = Query(default=20, ge=1, le=100),
    language: str | None = None,
    review_result: str | None = None,
    service: ReviewService = Depends(get_review_service),
) -> list[ReviewResponse]:
    return service.list_reviews(limit=limit, language=language, review_result=review_result)


@router.get("/api/v1/reviews/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    record = service.get_review(review_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Review not found.")
    return record
