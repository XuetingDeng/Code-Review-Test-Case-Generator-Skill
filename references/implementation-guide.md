# Implementation Guide

## API Contract

- `POST /api/v1/reviews`: create a review for a code snippet or git diff.
- `GET /api/v1/reviews`: list recent review records with optional `limit`, `language`, and `review_result`.
- `GET /api/v1/reviews/{review_id}`: fetch one review record.
- `GET /health`: return `{"status": "ok"}`.

## Request Rules

- `language`: one of `python`, `java`, `javascript`, `typescript`, `go`.
- `review_type`: `code_snippet` or `git_diff`; MVP can focus on `code_snippet`.
- `code`: non-empty, max 20,000 characters.
- `focus`: non-empty list from `bug`, `edge_case`, `exception`, `maintainability`, `security`, `test`.
- `generate_test_code`: whether generated unit test code should be requested from the LLM.

## Analysis Pipeline

1. Validate request.
2. Run deterministic rules.
3. Build a strict JSON prompt for Qwen.
4. Parse and validate LLM JSON into `ReviewResult`.
5. Retry once with a repair prompt if parsing fails.
6. Use fallback result if provider or validation still fails.
7. Merge deterministic and LLM findings, de-duplicating by type and description.
8. Reclassify the final review result deterministically.
9. Save full review metadata to SQLite.

## Deterministic Risk Rules

Python:

- Bare `except:`.
- `except Exception` without logging or re-raising.
- Division without an obvious zero check.
- List indexing without an obvious bounds check.
- Dictionary key access without `.get()` or key membership check.
- `open()` without a context manager.
- `eval()` or `exec()`.
- SQL query string concatenation or interpolation.

Java:

- Possible division by zero.
- `Optional.get()` without `isPresent` or `orElse`.
- `list.get(index)` without bounds checks.
- Catching `Exception` with an empty body.
- Possible null pointer from method calls without null checks.
- SQL string concatenation.
- Public method inputs without visible validation.

## Result Classification

- `HIGH_RISK`: any high `SECURITY`, `BUG`, or `EXCEPTION`; dangerous functions; unsafe SQL concatenation; or LLM high-risk classification.
- `NEEDS_CHANGES`: any medium/high risk, missing important tests, fallback result, or significant maintainability issue.
- `PASS`: no medium/high risks, meaningful test cases exist, and no high-risk signals.

## Persistence

Persist `language`, `review_type`, `code`, `focus`, `summary`, `risks`, `test_cases`, `test_code`, `review_result`, `fallback_used`, `llm_raw_response`, `error_message`, and `created_at`.

Store JSON-like fields as JSON strings in SQLite.

## Testing

Use mocked LLM clients. Cover:

- Rule analyzer findings for Python and Java.
- Parser behavior for valid JSON, markdown-wrapped JSON, invalid JSON, missing fields, and enum errors.
- Fallback with and without rule findings.
- Result merger high, medium, and pass classifications.
- API create/list/detail flows and fallback on invalid LLM output.
