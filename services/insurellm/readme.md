# insurellm

RAG microservice of the **[Portfolio microservices hub](../../readme.md)**. It
answers natural-language questions about the fictional *Insurellm* company,
grounding each answer in a domain knowledge base (LangChain + Chroma + OpenAI).

Originally a standalone RAG project, it has been refactored to the hub's
production microservice layout: the RAG logic lives under `ai/`, wrapped by a
thin `webserver` layer (app factory, probes, DI, domain-error envelope).

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/ping` | Liveness probe |
| `GET` | `/insurellm/api/v1/health` | Health check |
| `GET` | `/insurellm/api/v1/status` | Service metadata |
| `POST` | `/insurellm/api/v1/query` | Grounded answer over the knowledge base |

### `POST /query`

```jsonc
// request
{ "question": "What is Insurellm?" }

// response
{ "answer": "Insurellm is ...", "sources": ["assets/knowledge-base/company/overview.md"] }
```

Requires an `OPENAI_API_KEY` (chat model). Without it — or without the ML
dependencies installed — the endpoint returns `503 rag_unavailable`, so the hub
stays demonstrable when this service is not configured.

## Architecture

```text
src/backend/
├─ __main__.py                 # app factory (get_app) + lifespan + uvicorn
├─ ai/                         # the RAG core (vendored project code)
│  ├─ pipeline.py              #   build_rag(): indexing → retrieval → generation
│  ├─ constants.py             #   paths, model, lazy embeddings
│  ├─ indexing/                #   document loading + LLM-assisted chunking
│  ├─ retrieval/retriever.py   #   context retrieval
│  └─ llm/rag.py               #   grounded answer generation
└─ webserver/
   ├─ __init__.py              # facade: get_configs / get_logger / Configs
   ├─ configs/configs.py       # Pydantic config
   ├─ configurations.py        # env-driven loader
   ├─ dependency/deps.py       # DI
   ├─ errors.py                # domain errors + HTTP envelope
   ├─ models/query.py          # request/response models
   ├─ routers/                 # alive · health · status · query
   └─ services/rag_service.py  # lazy-builds and caches the pipeline
```

The pipeline is imported and built **lazily** on the first query, so the app
and its probe tests import without the ML stack.

## Run

```bash
uv sync
uv run pytest -q                 # probe tests (no key, no cost)
OPENAI_API_KEY=sk-... uv run python -m backend   # http://localhost:5001/ping
```

Knowledge base lives under [`assets/knowledge-base/`](assets/knowledge-base).
The first query builds a local Chroma store under `assets/vector_db`.
