# portfolio-assistant

RAG microservice of the **[Portfolio microservices hub](../../readme.md)**. It
answers natural-language questions about Mario Avolio's professional profile --
bio, skills, projects, experience, education, and publications -- grounding each
answer in a local knowledge base (LangChain + Chroma + OpenAI).

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/ping` | Liveness probe |
| `GET` | `/portfolio-assistant/api/v1/health` | Health check |
| `GET` | `/portfolio-assistant/api/v1/status` | Service metadata |
| `GET` | `/portfolio-assistant/api/v1/ready` | Readiness probe |
| `POST` | `/portfolio-assistant/api/v1/query` | Grounded answer over the knowledge base |

### `POST /query`

```jsonc
// request
{ "question": "What technologies does Mario know?" }

// response
{ "answer": "Mario's primary stack is ...", "sources": ["assets/knowledge-base/skills/tech-stack.md"] }
```

Requires an API key for the configured provider (see LLM Provider below).
Without it the endpoint returns \`503 rag_unavailable\` -- the hub stays demonstrable.

## Architecture

```text
src/portfolio_assistant/
├─ __main__.py                 # app factory (get_app) + lifespan + uvicorn
├─ ai/                         # the RAG core
│  ├─ pipeline.py              #   build_rag(): indexing + retrieval + generation
│  ├─ constants.py             #   paths, model, lazy embeddings
│  ├─ indexing/                #   document loading + chunking strategies
│  ├─ retrieval/retriever.py   #   context retrieval
│  └─ llm/rag.py               #   grounded answer generation
└─ webserver/
   ├─ __init__.py              # facade: get_configs / get_logger / Configs
   ├─ configs/configs.py       # Pydantic config
   ├─ configs/files/local.yml  # non-secret config (app, prefix, rag block)
   ├─ configurations.py        # cached loader: defaults + YAML overlay
   ├─ dependency/deps.py       # DI
   ├─ errors.py                # domain errors + HTTP envelope
   ├─ models/query.py          # request/response models
   ├─ routers/                 # alive + health + ready + status + query
   └─ services/rag_service.py  # lazy-builds and caches the pipeline
```

## LLM Provider

portfolio-assistant supports three providers, controlled via `llm_provider` in
`src/portfolio_assistant/webserver/configs/files/local.yml`:

| Provider | `llm_provider` | Model | API key |
| --- | --- | --- | --- |
| OpenAI (default) | `openai` | `gpt-4.1-nano` | `OPENAI_API_KEY` |
| Google | `google` | `gemini-2.0-flash` | `GOOGLE_API_KEY` (Google AI Studio) |
| HuggingFace | `hf` | `HuggingFaceH4/zephyr-7b-beta` | `HF_TOKEN` |

Embeddings are independent of `llm_provider` -- set via `rag.embeddings`.

## Knowledge base

```text
assets/knowledge-base/
  profile/          ← bio.md, contact.md
  skills/           ← tech-stack.md, specializations.md
  projects/         ← ai-microservices-hub.md, future-work.md
  experience/       ← machine-learning-reply.md, research-fellow.md
  education/        ← msc-bicocca.md, bsc-calabria.md
  publications/     ← iciap-2025.md, kr-2023.md
```

The first query builds a Chroma vector store under `assets/vector_db` (git-ignored)
and reuses it on subsequent runs.

## Run

```bash
uv sync
uv run python -m pytest -q              # probe tests (no key, no cost)
OPENAI_API_KEY=sk-... uv run python -m portfolio_assistant   # http://localhost:5001/ping
```
