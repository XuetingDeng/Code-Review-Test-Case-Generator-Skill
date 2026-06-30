import json

import pytest

from app.llm.output_parser import LLMOutputParser


def valid_payload():
    return {
        "summary": "ok",
        "risks": [],
        "test_cases": [{"name": "test_ok", "input": "x", "expected": "y", "reason": "coverage"}],
        "test_code": None,
        "review_result": "PASS",
    }


def test_parse_valid_json():
    result = LLMOutputParser().parse(json.dumps(valid_payload()))
    assert result.review_result == "PASS"


def test_parse_markdown_wrapped_json():
    result = LLMOutputParser().parse(f"```json\n{json.dumps(valid_payload())}\n```")
    assert result.summary == "ok"


def test_invalid_json_raises():
    with pytest.raises(ValueError):
        LLMOutputParser().parse("{bad")


def test_missing_required_fields_raises():
    with pytest.raises(ValueError):
        LLMOutputParser().parse(json.dumps({"summary": "missing"}))


def test_invalid_enum_raises():
    payload = valid_payload()
    payload["review_result"] = "MAYBE"
    with pytest.raises(ValueError):
        LLMOutputParser().parse(json.dumps(payload))
