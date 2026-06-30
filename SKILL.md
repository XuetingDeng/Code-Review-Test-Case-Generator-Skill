---
name: code-review-test-case-generator
description: Build, extend, or maintain a FastAPI-based AI Code Review and Test Case Generator that reviews code snippets or git diffs, detects bugs, edge cases, exception handling issues, maintainability and security risks, generates recommended test cases or unit test code, validates Qwen LLM JSON output, falls back to deterministic rule checks, and persists review history in SQLite. Use when the user asks for an AI code review backend, code review API, test case generator, Qwen-assisted code analysis, rule-based code risk analysis, or implementation based on this repository's docs/EDD.md.
---

# Code Review & Test Case Generator

Use this skill to create or evolve a backend service that accepts code or diffs, combines deterministic rule checks with Qwen semantic review, validates LLM output, generates test cases, stores review history, and returns a structured result.

## Quick Start

1. Read [docs/EDD.md](docs/EDD.md) for the complete engineering design when the user asks for architecture-level changes.
2. Read [references/implementation-guide.md](references/implementation-guide.md) for the compact execution guide and key invariants.
3. Copy or adapt [assets/code-review-api-template](assets/code-review-api-template) when bootstrapping a project implementation.
4. Preserve the provider boundary in `app/llm/base.py`; add new LLM providers behind the same interface.
5. Prefer tests with mocked LLM behavior. Do not require live Qwen credentials for unit or integration tests.

## Expected Workflow

When implementing the backend:

1. Validate input with Pydantic before any LLM call.
2. Run `RuleAnalyzer` first and keep its findings even if the LLM succeeds.
3. Call Qwen through `LLMClient` only after deterministic checks complete.
4. Parse LLM output as strict JSON and validate it with `ReviewResult`.
5. Retry once with a repair prompt when the first LLM response is invalid.
6. Build a fallback result from rule findings when LLM parsing or provider calls fail.
7. Merge rule and LLM findings, then classify final result using deterministic severity rules.
8. Persist request, output, raw LLM response, fallback status, and errors in SQLite.
9. Return API responses without exposing secrets or unvalidated LLM content.

## Implementation Notes

- MVP language support: Python and Java rules; schemas may accept Python, Java, JavaScript, TypeScript, and Go for forward compatibility.
- MVP review type: `code_snippet`; keep `git_diff` in schemas but reject or treat as a future extension unless implemented.
- Treat `eval`, `exec`, unsafe SQL concatenation, unvalidated command execution, high BUG, high EXCEPTION, and high SECURITY as `HIGH_RISK`.
- Return `NEEDS_CHANGES` instead of `PASS` when the review lacks meaningful test cases or contains medium risks.
- Do not log full source code in production mode. Never log API keys.

## Bundled Resources

- `assets/code-review-api-template/`: runnable FastAPI implementation with tests, Dockerfile, Compose file, and `.env.example`.
- `scripts/copy_template.py`: copies the template into a target directory without overwriting existing files unless `--force` is used.
- `references/implementation-guide.md`: concise reference for endpoints, models, validation, fallback, and tests.

## Validation

This repository is the Skill package. The runnable FastAPI project lives in
`assets/code-review-api-template/`, so run implementation checks from that
directory:

```bash
cd assets/code-review-api-template
python -m pytest
```

If dependencies are not installed, create a virtual environment and install the
template requirements from the same directory:

```bash
cd assets/code-review-api-template
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```
