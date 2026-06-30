# AI Code Review & Test Case Generator API

FastAPI backend for reviewing code snippets, generating test cases, validating Qwen JSON output, falling back to deterministic rules, and storing review history in SQLite.

## Run Locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Test

```bash
python -m pytest
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```
