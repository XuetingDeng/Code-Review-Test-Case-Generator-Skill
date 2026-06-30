from app.core.logging import get_logger
from app.db.repository import ReviewRepository, record_to_response
from app.llm.base import LLMClient
from app.llm.output_parser import LLMOutputParser
from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.fallback_builder import FallbackBuilder
from app.services.result_merger import ResultMerger
from app.services.rule_analyzer import RuleAnalyzer

logger = get_logger(__name__)


class ReviewService:
    def __init__(self, repository: ReviewRepository, llm_client: LLMClient):
        self.repository = repository
        self.llm_client = llm_client
        self.rule_analyzer = RuleAnalyzer()
        self.parser = LLMOutputParser()
        self.fallback_builder = FallbackBuilder()
        self.result_merger = ResultMerger()

    def create_review(self, request: ReviewRequest) -> ReviewResponse:
        rule_findings = self.rule_analyzer.analyze(request)
        raw_response: str | None = None
        fallback_used = False
        error_message: str | None = None

        try:
            raw_response = self.llm_client.analyze_code(request, rule_findings)
            parsed = self.parser.parse(raw_response)
        except Exception as first_error:
            try:
                repaired = self.llm_client.repair_json(raw_response or "", str(first_error))
                raw_response = repaired
                parsed = self.parser.parse(repaired)
            except Exception as fallback_error:
                fallback_used = True
                error_message = str(fallback_error)
                parsed = self.fallback_builder.build(request, rule_findings, fallback_error)

        final_result = self.result_merger.merge(rule_findings, parsed)
        try:
            record = self.repository.save(
                request=request,
                result=final_result,
                raw_llm_response=raw_response,
                fallback_used=fallback_used,
                error_message=error_message,
            )
        except Exception as exc:
            logger.exception("Failed to save review record")
            raise RuntimeError("Failed to save review record.") from exc

        logger.info(
            "review_created language=%s review_type=%s code_length=%s focus=%s fallback_used=%s review_result=%s error=%s",
            request.language,
            request.review_type,
            len(request.code),
            request.focus,
            fallback_used,
            final_result.review_result,
            error_message,
        )
        return record_to_response(record)

    def list_reviews(self, limit: int, language: str | None, review_result: str | None) -> list[ReviewResponse]:
        return [record_to_response(record) for record in self.repository.list(limit, language, review_result)]

    def get_review(self, review_id: int) -> ReviewResponse | None:
        record = self.repository.get(review_id)
        return record_to_response(record) if record else None
