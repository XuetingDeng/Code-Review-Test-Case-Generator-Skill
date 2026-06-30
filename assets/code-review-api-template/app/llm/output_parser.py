import json
import re

from pydantic import ValidationError

from app.schemas.review import ReviewResult


class LLMOutputParser:
    def parse(self, raw_response: str) -> ReviewResult:
        payload = self._extract_json(raw_response)
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON: {exc}") from exc
        try:
            return ReviewResult.model_validate(data)
        except ValidationError as exc:
            raise ValueError(f"Invalid review schema: {exc}") from exc

    def _extract_json(self, raw_response: str) -> str:
        text = raw_response.strip()
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            return fenced.group(1)
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in LLM response.")
        return text[start : end + 1]
