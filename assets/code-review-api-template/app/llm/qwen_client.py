import httpx

from app.llm.base import LLMClient
from app.llm.prompt_builder import build_repair_prompt, build_review_prompt
from app.schemas.review import ReviewRequest, RiskItem


class QwenClient(LLMClient):
    def __init__(self, api_key: str, base_url: str, model: str, timeout_seconds: int):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def analyze_code(self, request: ReviewRequest, rule_findings: list[RiskItem]) -> str:
        prompt = build_review_prompt(request, rule_findings)
        return self._chat(prompt)

    def repair_json(self, invalid_response: str, error: str) -> str:
        return self._chat(build_repair_prompt(invalid_response, error))

    def _chat(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("QWEN_API_KEY is not configured.")
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
