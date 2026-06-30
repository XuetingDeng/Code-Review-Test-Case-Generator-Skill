from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ReviewRecord(Base):
    __tablename__ = "review_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    language: Mapped[str] = mapped_column(String(32), index=True)
    review_type: Mapped[str] = mapped_column(String(32))
    code: Mapped[str] = mapped_column(Text)
    focus: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    risks: Mapped[str] = mapped_column(Text)
    test_cases: Mapped[str] = mapped_column(Text)
    test_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_result: Mapped[str] = mapped_column(String(32), index=True)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    llm_raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
