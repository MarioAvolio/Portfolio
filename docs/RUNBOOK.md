# Runbook

How to run, test and operate the hub. Every service uses
[uv](https://docs.astral.sh/uv/).

## Prerequisites

* Python >= 3.12
* [uv](https://docs.astral.sh/uv/getting-started/installation/)
* Docker (optional, for the composed run)

## Run the whole hub

```bash
docker compose up --build
# gateway: http://localhost:8000/gateway/api/v1/services
# console: http://localhost:8000/ui/
```

`docker compose up` starts `gateway`, `portfolio-assistant`, `deep-research`,
and `market-sentinel`. The latter three require `OPENAI_API_KEY` for their
functional endpoints; `market-sentinel` also needs `SERPER_API_KEY`.

Route a query through the gateway:

```bash
curl -X POST localhost:8000/gateway/api/v1/services/portfolio-assistant/query \
  -H 'content-type: application/json' \
  -d '{"question": "What technologies does Mario know?"}'
```

## Use the console

Open `http://localhost:8000/ui/` to use the static web console.
It lists registered services with live health, lets you send a query to any
service (prefilled from its `query_example`), and automatically polls async
jobs by their `job_id` until completion, showing status transitions
(pending -> running -> done).
It is a thin read-oriented client with no business logic and no auth (local demo only).

## Run a single service

```bash
cd <service>
uv sync                           # create/update venv from lockfile
uv run pytest -q                  # tests
uv run ruff check .               # lint
uv run python -m <package_name>   # serve
```

Package names per service:

| Service | Package name | Port | Needs API key |
| --- | --- | --- | --- |
| gateway | `gateway` | 8000 | no |
| portfolio-assistant | `portfolio_assistant` | 5001 | `OPENAI_API_KEY` |
| deep-research | `deep_research` | 5002 | `OPENAI_API_KEY` |
| market-sentinel | `market_sentinel` | 5003 | `OPENAI_API_KEY` + `SERPER_API_KEY` |

Example (portfolio-assistant):
```bash
cd services/portfolio-assistant
export OPENAI_API_KEY=sk-...
uv run python -m portfolio_assistant
```

## Workspace sync

The repo uses a uv workspace (`pyproject.toml` at root). A single command
installs all services:

```bash
uv sync
```

## Configuration and secrets

Non-secret settings live in each service's
`src/<package>/webserver/configs/files/local.yml` and are loaded automatically
when `ENVIRONMENT=local` (the default). Edit that YAML to change behaviour.

**Secrets** (API keys) come from the environment only -- never hard-code them
and never put them in YAML:

```bash
export OPENAI_API_KEY=sk-...
export SERPER_API_KEY=...      # market-sentinel only
uv run python -m market_sentinel
```

## Per-service notes

### portfolio-assistant

Tuned via the `rag` block in `configs/files/local.yml`:

* `rag.llm_provider: openai` (default, gpt-4.1-nano) -- also supports `google`,
  `hf`, `ollama`.
* `rag.embeddings: openai` (default) -- `hf` uses local embeddings
  (install with `uv sync --extra hf`).
* `rag.chunking: simple` (default) -- `llm` produces richer chunks at one model
  call per document.
* The vector store is built once under `assets/vector_db` (git-ignored) and
  reused on subsequent runs.

Google provider: key must be created at aistudio.google.com (NOT Google Cloud
Console). Starts with `AIza`.

Ollama provider: `ollama pull llama3.2:1b && ollama serve`, then
`uv sync --extra ollama`.

### deep-research

Runs the multi-agent workflow (planner -> web searches -> writer). Needs
`OPENAI_API_KEY`.

Two query modes:

* **Synchronous** -- `POST /deep-research/api/v1/query` returns the report inline.
* **Async (job-based)** -- `POST /deep-research/api/v1/research` returns a `job_id`
  (`202 Accepted`); poll `GET /deep-research/api/v1/research/jobs/{job_id}` until
  `status` is `done`. The job response includes agent `steps` and the final
  `report`.

### market-sentinel

Two-agent CrewAI crew (market_researcher via SerperDev + strategic_analyst).
Reports persisted to SQLite.

Needs `OPENAI_API_KEY` + `SERPER_API_KEY`.

API:
* `POST /market-sentinel/api/v1/research` -> 202 + `job_id`
* `GET /market-sentinel/api/v1/research/jobs/{job_id}` -- poll until done
* `GET /market-sentinel/api/v1/research/history` -- list recent completed reports

## CI

`.github/workflows/ci.yml` runs lint + tests for every service:

* `gateway` -- full `uv sync --frozen` + ruff + mypy + bandit + pytest
* `heavy-services` (portfolio-assistant, deep-research) -- minimal pip install +
  ruff + bandit + pytest (probe tests only; AI cores imported lazily)

## Tests at a glance

```bash
# Run all services from repo root
cd gateway && uv run pytest -q && cd ..
cd services/portfolio-assistant && uv run pytest -q && cd ../..
cd services/deep-research && uv run pytest -q && cd ../..
```

Or per service quality pipeline:
```bash
cd <service>
uv run ruff check src/ && uv run ruff format src/ --check
uv run mypy src/<package>/webserver/ --ignore-missing-imports
uv run bandit -r src/ -ll -q -c pyproject.toml
uv run pytest -q --cov=src/ --cov-report=term-missing
```
