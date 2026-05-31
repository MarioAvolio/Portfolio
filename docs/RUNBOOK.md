# Runbook

How to run, test and operate the hub. Every service uses
[uv](https://docs.astral.sh/uv/).

## Prerequisites

* Python ≥ 3.11 (≥ 3.12 for `deep-research`)
* [uv](https://docs.astral.sh/uv/getting-started/installation/)
* Docker (optional, for the composed run)

## Run the whole hub (free path)

```bash
docker compose up --build
# gateway:  http://localhost:8000/gateway/api/v1/services
```

`docker compose up` starts the `gateway` and the free `text-intelligence`
service. The heavy services run locally (below).

Route a query through the gateway:

```bash
curl -X POST localhost:8000/gateway/api/v1/services/text-intelligence/query \
  -H 'content-type: application/json' -d '{"text": "I love this product."}'
```

## Run a single service

```bash
cd <service>
uv sync                       # create venv from the lockfile
uv run pytest -q              # tests
uv run ruff check .           # lint
uv run python -m backend      # serve
```

| Service | Port | Free without a key? |
| --- | --- | --- |
| gateway | 8000 | yes |
| text-intelligence | 5000 | yes (mock provider) |
| insurellm | 5001 | no — needs `OPENAI_API_KEY` |
| deep-research | 5002 | no — needs `OPENAI_API_KEY` |

## Configuration & secrets

Non-secret settings live in each service's `src/backend/webserver/configs/files/local.yml`
and are loaded automatically (`ENVIRONMENT=local`). Edit that YAML to change
behaviour — there is no `.env` for configuration.

**Secrets** (API keys) are read from the environment only — never hard-code them
and never put them in YAML. Export them in your shell (a local, git-ignored
`.env` is fine for convenience, but it is never committed):

```bash
cd services/insurellm
export OPENAI_API_KEY=sk-...
uv run python -m backend
```

## Per-service notes

### text-intelligence
The provider is set in `configs/files/local.yml` (`provider.name: mock` by
default — no key needed). Real providers plug in behind the `LLMProvider`
interface; their API key is read from the environment.

### insurellm
Tuned via the `rag` block in `configs/files/local.yml`:
* `rag.embeddings: openai` (default) — light, no local ML stack; `hf` uses local
  embeddings (install with `uv sync --extra hf`).
* `rag.chunking: simple` (default) indexes for free; `llm` produces richer chunks
  at one model call per document.
* `rag.max_documents` caps the indexed corpus (`null` = all).
* The vector store is built once under `assets/vector_db` (git-ignored) and
  reused on subsequent runs.

### deep-research
Runs the multi-agent workflow (planner → web searches → writer). Needs
`OPENAI_API_KEY`; a single run performs several model calls and web searches.

## CI

`.github/workflows/ci.yml` runs lint + tests for every service. The lightweight
services use a locked `uv sync`; the heavy services verify their microservice
surface with a minimal toolchain (their AI cores are imported lazily).

## Tests at a glance

```bash
# from the repo root
for s in gateway services/text-intelligence services/insurellm services/deep-research; do
  ( cd "$s" && uv run pytest -q )
done
```
