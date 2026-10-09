# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

FastAPI + SQLite backend for an AI test-case generator. It ingests customer requirement/QBP
Excel workbooks, uses an LLM to generate traceable test cases from extracted rules, lets a
reviewer approve them, converts approved cases into Playwright TypeScript specs, and runs those
specs on demand. This `backend/` directory is one of several siblings under `Automation/`
(`automation/` = Node/Playwright project, `frontend/` = React/Vite UI, `samples/`, `tools/`).
See `../README.md` for the full multi-process setup, corporate-proxy (Zscaler) TLS workarounds,
and the portable Node install under `../tools/`.

## Commands

Run everything through the venv interpreter (`.venv/Scripts/python`), not a bare `python`.

```sh
# Install deps (one-time)
./.venv/Scripts/pip install -r requirements.txt

# Run the API (no --reload; see note below)
./.venv/Scripts/python -m uvicorn app.main:app --port 8000

# Health check / API docs
curl http://localhost:8000/health          # {"status":"ok"}
# http://localhost:8000/docs                (Swagger UI)

# Extract rule tables from a workbook standalone (CLI in extract_rules.py)
./.venv/Scripts/python -m app.services.extract_rules <workbook.xlsx> [-o out.json]
```

There is **no test suite, linter, or formatter configured** in this backend — don't invent
`pytest`/`ruff`/`black` commands.

**Avoid `--reload`:** on the target (Windows) machine uvicorn's reload watcher can leave a
stale child process bound to port 8000, silently serving old code. If a restart seems to have
no effect, check what's actually on the port before assuming your change is wrong (PowerShell
`Get-NetTCPConnection -LocalPort 8000`).

## Configuration

`app/config.py` loads from `backend/.env` (see `.env.example`). Required: `BEDROCK_API_KEY`,
`BEDROCK_MODEL_ID` (an inference-profile ARN — the region is parsed out of it unless
`AWS_REGION` is set). `ai_client.py` copies `BEDROCK_API_KEY` into `AWS_BEARER_TOKEN_BEDROCK`
so boto3's `bedrock-runtime` client authenticates. `LOG_LEVEL=DEBUG` logs full prompts and raw
Converse responses.

> Note: `../README.md` still describes the older Anthropic Files API + `ANTHROPIC_API_KEY`
> design. The backend code has since moved to **AWS Bedrock Converse**; trust the code in
> `app/services/ai_client.py` over the README on anything LLM-related.

## Architecture

The data model (`app/models.py`) encodes the end-to-end pipeline, and each stage is a router:

```
Customer ─< Document ─< Rule ─< TestCase ─1 PlaywrightScript
```

The core flow, in order:

1. **Upload** (`routers/documents.py`): accepts `.xlsx` only. `services/doc_parser.py` flattens
   every sheet to pipe-delimited plain text (stored on `Document.extracted_text`); in the same
   request `services/extract_rules.py` scans each sheet for a header row with `Rule Name` +
   `Discreption` (misspelling intentional — it's the source column name; aliases are defined in
   `extract_rules.COLUMN_ALIASES`) and persists one `Rule` per data row.
2. **List rules** (`routers/rules.py`): returns rules from the customer's *most recently
   uploaded* document only.
3. **Generate test cases** (`routers/testcases.py` → `ai_client.generate_test_cases`): one rule
   at a time. The model is forced to call a `record_test_cases` tool whose input schema is the
   Pydantic `GeneratedTestCaseList` made strict by `ai_client._strict_schema` (every object gets
   `additionalProperties: false` + all props required). Rows are saved with `status="draft"`.
4. **Review**: edit via `PATCH /test-cases/{id}`, then `POST /test-cases/{id}/approve`.
5. **Generate script** (`routers/codegen.py` → `ai_client.generate_playwright_code`): requires
   `status == "approved"`. Produces one `.spec.ts` as plain text (markdown fences stripped),
   stored on `PlaywrightScript`. The frontend offers it as a manual download; the backend no
   longer executes specs (the run/Playwright-runner feature was removed).
6. **Report** (`routers/reports.py`): server-rendered HTML traceability view (test case ↔
   requirement trace), plus total/approved/draft counts.

### Things worth knowing

- **The configured Bedrock model rejects Converse `document` content blocks**
  (`ValidationException: This model doesn't support documents`). That's why documents are
  reduced to text at upload time and sent as plain `{"text": ...}` blocks — see the docstrings
  in `ai_client._document_blocks` and `doc_parser.py`. Don't try to re-add native document
  ingestion without changing the model.
- **DB schema is created with `Base.metadata.create_all` at startup** (`app/main.py`), with no
  migration tool. Changing a column in `models.py` won't alter the existing `automation.db` —
  delete the file (or add migration tooling) when you change the schema.
- **Everything runs synchronously** on the request thread, including multi-second Bedrock calls.
  There is no background job queue.
- CORS is hardcoded to allow `http://localhost:5173` (the Vite frontend) in `app/main.py`.
- `DELETE /customers/{id}` cascades to the customer's documents, rules, test cases, and scripts
  via the `cascade="all, delete-orphan"` relationships in `models.py`.
