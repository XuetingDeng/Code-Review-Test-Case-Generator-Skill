# Engineering Design Document: Code Review & Test Case Generator Skill

## 1. Project Overview

### 1.1 Project Name

**Code Review & Test Case Generator Skill**

### 1.2 Goal

Build a practical developer productivity skill that helps users review code snippets or Git diffs, identify potential bugs, edge cases, exception handling issues, maintainability risks, and generate suggested test cases.

The skill should not blindly trust AI-generated output. It should combine rule-based checks, Qwen-based semantic analysis, structured output validation, fallback handling, and persistent review history.

### 1.3 Target Use Case

A developer pastes a code snippet or Git diff into the API. The system returns:

1. A short summary of what the code does.
2. Potential bugs and risks.
3. Edge cases that may be missing.
4. Exception handling issues.
5. Maintainability suggestions.
6. Recommended test cases.
7. Optional generated unit test code.
8. A final review result: `PASS`, `NEEDS_CHANGES`, or `HIGH_RISK`.

### 1.4 Why This Project Matters

This project is designed to demonstrate backend engineering ability in an AI Coding / Bot backend context.

It emphasizes:

* API design
* User request handling
* AI-assisted code analysis
* AI output validation
* Boundary condition detection
* Test case generation
* Logging and debugging
* Persistence with SQLite
* Dockerized deployment
* Maintainable backend architecture

---

## 2. Tech Stack

### 2.1 Backend

* Python 3.11+
* FastAPI
* Pydantic
* Uvicorn

### 2.2 LLM

* Qwen API

The project should implement a clean LLM client abstraction so the model provider can be replaced later.

### 2.3 Database

* SQLite
* SQLAlchemy ORM

SQLite is enough for the initial version because this is a lightweight local skill project.

### 2.4 Testing

* Pytest
* FastAPI TestClient
* Mocked LLM client for unit tests

### 2.5 Deployment

* Docker
* Docker Compose

---

## 3. High-Level Architecture

```text
Client / User
    ↓
FastAPI Controller
    ↓
ReviewService
    ↓
Input Validation
    ↓
Rule-Based Analyzer
    ↓
Qwen LLM Analyzer
    ↓
LLM Output Parser
    ↓
Schema Validation
    ↓
Fallback / Retry Logic
    ↓
Result Aggregation
    ↓
SQLite Persistence
    ↓
Response
```

---

## 4. Core Features

### 4.1 Code Review API

Endpoint:

```text
POST /api/v1/reviews
```

Request body:

```json
{
  "language": "python",
  "code": "def divide(a, b):\n    return a / b",
  "review_type": "code_snippet",
  "focus": ["bug", "edge_case", "exception", "test"],
  "generate_test_code": true
}
```

Response body:

```json
{
  "review_id": 1,
  "summary": "The code defines a function that divides two numbers.",
  "risks": [
    {
      "type": "EXCEPTION",
      "level": "HIGH",
      "description": "The function does not handle division by zero.",
      "suggestion": "Check whether b is zero before performing division."
    }
  ],
  "test_cases": [
    {
      "name": "test_divide_normal_case",
      "input": "a=10, b=2",
      "expected": "5",
      "reason": "Covers the normal division path."
    },
    {
      "name": "test_divide_by_zero",
      "input": "a=10, b=0",
      "expected": "Raises ZeroDivisionError or returns a controlled error",
      "reason": "Covers the division-by-zero edge case."
    }
  ],
  "test_code": "def test_divide_normal_case():\n    assert divide(10, 2) == 5",
  "review_result": "NEEDS_CHANGES",
  "fallback_used": false,
  "created_at": "2026-06-28T12:00:00Z"
}
```

---

### 4.2 Review History API

Endpoint:

```text
GET /api/v1/reviews
```

Returns recent review records.

Query parameters:

```text
limit: int = 20
language: optional string
review_result: optional string
```

---

### 4.3 Review Detail API

Endpoint:

```text
GET /api/v1/reviews/{review_id}
```

Returns one stored review record.

---

### 4.4 Health Check API

Endpoint:

```text
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

## 5. Supported Inputs

### 5.1 Programming Languages

Initial version should support:

* Python
* Java
* JavaScript / TypeScript
* Go

The first implementation can focus on Python and Java. The design should allow adding more languages later.

### 5.2 Review Types

```text
code_snippet
git_diff
```

Initial version can support `code_snippet` first. `git_diff` can be added as a second milestone.

### 5.3 Focus Areas

Allowed values:

```text
bug
edge_case
exception
maintainability
security
test
```

---

## 6. Data Model

### 6.1 ReviewRecord

Table name:

```text
review_records
```

Fields:

```text
id: integer primary key
language: string
review_type: string
code: text
focus: text/json string
summary: text
risks: text/json string
test_cases: text/json string
test_code: text nullable
review_result: string
fallback_used: boolean
llm_raw_response: text nullable
error_message: text nullable
created_at: datetime
```

---

## 7. Pydantic Schemas

### 7.1 ReviewRequest

```python
class ReviewRequest(BaseModel):
    language: Literal["python", "java", "javascript", "typescript", "go"]
    code: str
    review_type: Literal["code_snippet", "git_diff"] = "code_snippet"
    focus: list[Literal[
        "bug",
        "edge_case",
        "exception",
        "maintainability",
        "security",
        "test"
    ]] = ["bug", "edge_case", "exception", "test"]
    generate_test_code: bool = True
```

Validation rules:

* `code` cannot be empty.
* `code` length should be limited, for example max 20,000 characters.
* `focus` cannot be empty.
* Unsupported language should return HTTP 422.

---

### 7.2 RiskItem

```python
class RiskItem(BaseModel):
    type: Literal[
        "BUG",
        "EDGE_CASE",
        "EXCEPTION",
        "MAINTAINABILITY",
        "SECURITY"
    ]
    level: Literal["LOW", "MEDIUM", "HIGH"]
    description: str
    suggestion: str
```

---

### 7.3 TestCaseItem

```python
class TestCaseItem(BaseModel):
    name: str
    input: str
    expected: str
    reason: str
```

---

### 7.4 ReviewResult

```python
class ReviewResult(BaseModel):
    summary: str
    risks: list[RiskItem]
    test_cases: list[TestCaseItem]
    test_code: str | None = None
    review_result: Literal["PASS", "NEEDS_CHANGES", "HIGH_RISK"]
```

---

### 7.5 ReviewResponse

```python
class ReviewResponse(ReviewResult):
    review_id: int
    fallback_used: bool
    created_at: datetime
```

---

## 8. Rule-Based Analyzer

The system should include a lightweight rule-based analyzer before or alongside Qwen.

### 8.1 Purpose

The rule-based analyzer should catch stable and common problems without relying on the LLM.

It improves reliability because deterministic checks can still return useful results when:

* Qwen API fails
* LLM returns invalid JSON
* LLM response times out
* LLM misses obvious issues

### 8.2 Python Rules

Detect common patterns:

1. Bare `except:`
2. `except Exception` without logging or re-raising
3. Division operation without obvious zero check
4. List indexing without obvious bounds check
5. Dictionary key access using `dict[key]` without `.get()` or key check
6. File open without context manager
7. Use of `eval` or `exec`
8. SQL string concatenation risk

### 8.3 Java Rules

Detect common patterns:

1. Possible division by zero
2. `Optional.get()` without `isPresent()` or `orElse`
3. `list.get(index)` without bounds check
4. Catching `Exception` and ignoring it
5. Possible null pointer risk
6. String concatenation in SQL query
7. Missing validation for public method inputs

### 8.4 Rule-Based Output Format

The rule analyzer should return a list of `RiskItem`.

Example:

```json
[
  {
    "type": "EXCEPTION",
    "level": "HIGH",
    "description": "Possible division by zero risk detected.",
    "suggestion": "Validate the denominator before division."
  }
]
```

---

## 9. Qwen LLM Analyzer

### 9.1 LLM Client Interface

Create an abstraction:

```python
class LLMClient:
    def analyze_code(self, request: ReviewRequest, rule_findings: list[RiskItem]) -> str:
        ...
```

Concrete implementation:

```python
class QwenClient(LLMClient):
    def analyze_code(self, request: ReviewRequest, rule_findings: list[RiskItem]) -> str:
        ...
```

For testing:

```python
class MockLLMClient(LLMClient):
    def analyze_code(self, request: ReviewRequest, rule_findings: list[RiskItem]) -> str:
        ...
```

### 9.2 Prompt Requirements

The prompt must instruct Qwen to output strict JSON only.

The JSON should match:

```json
{
  "summary": "string",
  "risks": [
    {
      "type": "BUG | EDGE_CASE | EXCEPTION | MAINTAINABILITY | SECURITY",
      "level": "LOW | MEDIUM | HIGH",
      "description": "string",
      "suggestion": "string"
    }
  ],
  "test_cases": [
    {
      "name": "string",
      "input": "string",
      "expected": "string",
      "reason": "string"
    }
  ],
  "test_code": "string or null",
  "review_result": "PASS | NEEDS_CHANGES | HIGH_RISK"
}
```

### 9.3 Prompt Template

Use a separate prompt builder file.

Example:

````text
You are a senior backend engineer and code reviewer.

Review the following code.

Language:
{language}

Review type:
{review_type}

User focus areas:
{focus}

Rule-based findings:
{rule_findings}

Code:
```{language}
{code}
````

Return strict JSON only.
Do not include markdown.
Do not include explanations outside JSON.

JSON schema:
{
"summary": "string",
"risks": [
{
"type": "BUG | EDGE_CASE | EXCEPTION | MAINTAINABILITY | SECURITY",
"level": "LOW | MEDIUM | HIGH",
"description": "string",
"suggestion": "string"
}
],
"test_cases": [
{
"name": "string",
"input": "string",
"expected": "string",
"reason": "string"
}
],
"test_code": "string or null",
"review_result": "PASS | NEEDS_CHANGES | HIGH_RISK"
}

````

---

## 10. LLM Output Validation

### 10.1 Parser

Create a parser that:

1. Extracts JSON from the LLM response.
2. Parses it into Python dict.
3. Validates it using `ReviewResult`.
4. Returns a typed object.

### 10.2 Invalid Output Handling

If Qwen returns invalid JSON:

1. Retry once with a stricter repair prompt.
2. If retry fails, use fallback result.

### 10.3 Fallback Result

Fallback should use rule-based findings.

If rule-based findings are not empty:

```text
review_result = NEEDS_CHANGES or HIGH_RISK
````

If there are no rule-based findings:

```text
review_result = NEEDS_CHANGES
```

Fallback response example:

```json
{
  "summary": "LLM analysis failed. This fallback result is based on deterministic rule checks.",
  "risks": [],
  "test_cases": [
    {
      "name": "test_normal_case",
      "input": "Provide representative valid input",
      "expected": "Expected successful output",
      "reason": "Basic happy path coverage"
    }
  ],
  "test_code": null,
  "review_result": "NEEDS_CHANGES"
}
```

---

## 11. Review Result Classification

Final result should follow these rules:

### 11.1 HIGH_RISK

Return `HIGH_RISK` if:

* Any risk has level `HIGH` and type is `SECURITY`, `BUG`, or `EXCEPTION`.
* The code contains obvious dangerous functions such as `eval`, `exec`, unsafe SQL concatenation, or unvalidated command execution.
* LLM classifies it as `HIGH_RISK`.

### 11.2 NEEDS_CHANGES

Return `NEEDS_CHANGES` if:

* There are medium or high risks.
* Missing important test cases.
* Missing exception handling.
* Maintainability issues are significant.

### 11.3 PASS

Return `PASS` only if:

* No high risks.
* No medium risks.
* Test cases are provided.
* Code appears safe and maintainable for the given scope.

---

## 12. Service Design

### 12.1 ReviewService

Responsibilities:

1. Validate request.
2. Run rule-based analyzer.
3. Call Qwen.
4. Parse and validate LLM response.
5. Merge rule-based findings with LLM findings.
6. Determine final review result.
7. Save review record to SQLite.
8. Return response.

Pseudo logic:

```python
def create_review(request: ReviewRequest) -> ReviewResponse:
    rule_findings = rule_analyzer.analyze(request)

    try:
        raw_llm_response = llm_client.analyze_code(request, rule_findings)
        parsed_result = llm_output_parser.parse(raw_llm_response)
        fallback_used = False
    except Exception as e:
        parsed_result = fallback_builder.build(request, rule_findings, error=e)
        raw_llm_response = None
        fallback_used = True

    final_result = result_merger.merge(rule_findings, parsed_result)

    record = repository.save(
        request=request,
        result=final_result,
        raw_llm_response=raw_llm_response,
        fallback_used=fallback_used
    )

    return ReviewResponse(
        review_id=record.id,
        **final_result.model_dump(),
        fallback_used=fallback_used,
        created_at=record.created_at
    )
```

---

## 13. Project Structure

```text
code-review-skill/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── routes.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   ├── schemas/
│   │   ├── review.py
│   │   └── common.py
│   ├── services/
│   │   ├── review_service.py
│   │   ├── rule_analyzer.py
│   │   ├── result_merger.py
│   │   └── fallback_builder.py
│   ├── llm/
│   │   ├── base.py
│   │   ├── qwen_client.py
│   │   ├── mock_client.py
│   │   ├── prompt_builder.py
│   │   └── output_parser.py
│   └── utils/
│       └── json_utils.py
├── tests/
│   ├── test_api_reviews.py
│   ├── test_rule_analyzer.py
│   ├── test_output_parser.py
│   ├── test_fallback_builder.py
│   └── test_review_service.py
├── docs/
│   └── EDD.md
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 14. Environment Variables

Use `.env` for configuration.

`.env.example`:

```text
APP_ENV=dev
DATABASE_URL=sqlite:///./code_review_skill.db
QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=1
```

Never commit a real API key.

---

## 15. Docker Requirements

### 15.1 Dockerfile

The Dockerfile should:

1. Use a Python 3.11 slim base image.
2. Set working directory.
3. Install dependencies.
4. Copy project files.
5. Expose port 8000.
6. Run Uvicorn.

Expected command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 15.2 Docker Compose

`docker-compose.yml` should run the app with environment variables loaded from `.env`.

SQLite database can be stored in a mounted volume.

---

## 16. API Error Handling

The API should return clear errors.

### 16.1 Empty Code

Status:

```text
422
```

Message:

```json
{
  "detail": "Code cannot be empty."
}
```

### 16.2 Unsupported Language

Status:

```text
422
```

### 16.3 LLM Failure

The API should not fail directly if LLM fails. It should return fallback response with:

```json
{
  "fallback_used": true
}
```

### 16.4 Database Failure

Status:

```text
500
```

Message:

```json
{
  "detail": "Failed to save review record."
}
```

---

## 17. Logging

Use structured logs.

For every review request, log:

```text
request_id
language
review_type
code_length
focus
llm_latency_ms
fallback_used
review_result
error_message
```

Do not log secrets.

Do not log full code in production mode.

In development mode, code logging can be allowed only if explicitly enabled.

---

## 18. Testing Plan

### 18.1 Unit Tests

Test `RuleAnalyzer`:

* Python division by zero risk
* Python bare except
* Python eval / exec
* Java Optional.get risk
* Java SQL concatenation risk

Test `OutputParser`:

* Valid JSON response
* JSON wrapped in markdown
* Invalid JSON
* Missing required fields
* Invalid enum values

Test `FallbackBuilder`:

* Fallback with rule findings
* Fallback without rule findings
* Fallback review result classification

Test `ResultMerger`:

* High risk from rules should make final result `HIGH_RISK`
* Medium risk should make final result `NEEDS_CHANGES`
* Clean result can be `PASS`

### 18.2 Integration Tests

Test API endpoint:

```text
POST /api/v1/reviews
```

Cases:

1. Valid Python code.
2. Empty code.
3. Unsupported language.
4. Mock LLM returns invalid JSON.
5. Mock LLM timeout triggers fallback.
6. Review record is saved and can be fetched.

---

## 19. Minimum Viable Product Scope

### MVP Must Have

1. FastAPI backend.
2. `POST /api/v1/reviews`.
3. SQLite persistence.
4. Rule-based analyzer for Python.
5. Qwen client.
6. Strict JSON output parser.
7. Fallback handling.
8. Review history API.
9. Dockerfile.
10. Basic pytest tests.

### MVP Can Skip

1. Frontend UI.
2. Authentication.
3. GitHub integration.
4. Multi-user support.
5. Advanced static analysis.
6. Real execution of generated tests.

---

## 20. Future Enhancements

Possible future features:

1. Git diff review support.
2. GitHub PR comment generator.
3. JUnit / Pytest / Go test code generation.
4. Code complexity analysis.
5. Security-specific rules.
6. User accounts.
7. Review result dashboard.
8. VS Code extension.
9. CLI command:

```bash
code-review-skill review --file app.py --language python
```

10. Test execution sandbox.

---

## 21. Success Criteria

The project is successful if:

1. A user can submit code and receive structured review results.
2. The system can identify at least common bugs and edge cases.
3. Qwen output is validated before being returned.
4. Invalid LLM output does not crash the API.
5. Review history is stored in SQLite.
6. The app can run with Docker.
7. The core logic has unit tests.
8. The project can be explained as a practical AI Coding productivity skill.

---

## 22. Resume Positioning

This project should be positioned as:

**AI Code Review & Test Case Generator Skill**
Tech Stack: Python, FastAPI, Qwen, SQLite, SQLAlchemy, Pytest, Docker

Resume bullets:

* Built an AI-powered developer productivity skill that reviews code snippets, detects bugs, edge cases, exception handling issues, and maintainability risks.
* Integrated Qwen with a structured prompt and strict Pydantic schema validation to prevent malformed AI outputs from directly entering the backend workflow.
* Implemented a hybrid review pipeline combining rule-based static checks and LLM-based semantic analysis, improving reliability when AI output is incomplete or invalid.
* Designed fallback handling, request logging, and SQLite-based review history to support debugging and result traceability.
* Generated test case suggestions and optional unit test code covering normal paths, boundary inputs, exception paths, and regression scenarios.
