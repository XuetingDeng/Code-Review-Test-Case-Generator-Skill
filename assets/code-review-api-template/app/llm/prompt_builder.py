import json

from app.schemas.review import ReviewRequest, RiskItem


def build_review_prompt(request: ReviewRequest, rule_findings: list[RiskItem]) -> str:
    findings = json.dumps([item.model_dump() for item in rule_findings], ensure_ascii=False)
    test_code_instruction = "Include test_code when practical." if request.generate_test_code else "Set test_code to null."
    return f"""You are a senior backend engineer and code reviewer.

Review the following code.

Language:
{request.language}

Review type:
{request.review_type}

User focus areas:
{", ".join(request.focus)}

Rule-based findings:
{findings}

Code:
```{request.language}
{request.code}
```

{test_code_instruction}

Return strict JSON only.
Do not include markdown.
Do not include explanations outside JSON.

JSON schema:
{{
  "summary": "string",
  "risks": [
    {{
      "type": "BUG | EDGE_CASE | EXCEPTION | MAINTAINABILITY | SECURITY",
      "level": "LOW | MEDIUM | HIGH",
      "description": "string",
      "suggestion": "string"
    }}
  ],
  "test_cases": [
    {{
      "name": "string",
      "input": "string",
      "expected": "string",
      "reason": "string"
    }}
  ],
  "test_code": "string or null",
  "review_result": "PASS | NEEDS_CHANGES | HIGH_RISK"
}}
"""


def build_repair_prompt(invalid_response: str, error: str) -> str:
    return f"""Convert the following invalid model response into strict JSON that matches the required review schema.

Validation error:
{error}

Invalid response:
{invalid_response}

Return JSON only. No markdown."""
