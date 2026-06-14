# text-intelligence

First microservice of **[AI-Services-Hub](../readme.md)**. A FastAPI service that
turns free-form text into a structured analysis (summary, sentiment, tags,
language) through a **pluggable LLM provider**.

The layout mirrors the production microservice pattern: an app factory with a
lifespan hook, operational probes, a thin service layer, dependency-injected
providers, and a domain-error -> HTTP envelope translation.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/ping` | Liveness probe |
| `GET` | `/text-intelligence/api/v1/health` | Health check |
| `GET` | `/text-intelligence/api/v1/status` | Service metadata + active provider |
| `POST` | `/text-intelligence/api/v1/analyze` | Structured text analysis |

### `POST /analyze`

```jsonc
// request
{ "text": "I love this great product. It works really well." }

// response
{
  "summary": "I love this great product.",
  "sentiment": "positive",
  "tags": ["product", "works", "really", "well", "love"],
  "language": "en",
  "model": "mock-1"
}
```

## Architecture

```text
src/text_intelligence/
├─ __main__.py              # app factory (get_app) + lifespan + uvicorn
├─ ai/
│  └─ providers/            # LLMProvider abstraction
│     ├─ base.py            #   contract
│     └─ mock.py            #   zero-cost default impl
└─ webserver/
   ├─ __init__.py           # facade: get_configs / get_logger / Configs
   ├─ configs/configs.py    # Pydantic config models
   ├─ configurations.py     # env-driven loader (cached)
   ├─ dependency/deps.py    # DI: provider + service wiring
   ├─ errors.py             # domain errors + HTTP envelope
   ├─ models/analyze.py     # request/response models
   ├─ routers/              # alive + health + status + analyze
   └─ services/analysis.py  # business logic
```

The webserver layer depends only on the `LLMProvider` contract, so new backends
(Gemini, OpenAI, Azure OpenAI) plug in by adding one file and one branch in
`deps.py` -- no routing or service changes.

## Run

This project uses [**uv**](https://docs.astral.sh/uv/) as its environment and
dependency manager. The locked environment is reproducible from `uv.lock`.

```bash
# create the virtualenv and install everything from the lockfile
uv sync

# run tests (mock provider -> no API key, no cost)
uv run pytest -q

# serve locally
uv run python -m text_intelligence     # http://localhost:5000/ping

# or via Docker
docker compose up --build
```

Configuration lives in [`configs/files/local.yml`](src/text_intelligence/webserver/configs/files/local.yml)
(`app_name`, `api_prefix`, and the `provider` block -- `mock` by default). The
active environment is selected by `ENVIRONMENT` (default `local`). A provider's
API key, when needed, is read from the environment, not from the YAML.

## Status

Current scope: core routes on the **mock** provider. Real providers, object
storage and deployment land in later roadmap steps -- see the
[hub roadmap](../readme.md#roadmap).
