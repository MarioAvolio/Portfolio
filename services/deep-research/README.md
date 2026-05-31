# deep-research

Multi-agent research microservice of the
**[Portfolio microservices hub](../../readme.md)**. Given a research request it
plans searches, gathers web evidence in parallel and writes a structured
markdown report, using the OpenAI Agents SDK.

Originally a standalone Gradio app, it has been refactored to the hub's
production microservice layout: the agents live under `ai/`, wrapped by a thin
`webserver` layer (app factory, probes, DI, domain-error envelope).

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/ping` | Liveness probe |
| `GET` | `/deep-research/api/v1/health` | Health check |
| `GET` | `/deep-research/api/v1/status` | Service metadata |
| `POST` | `/deep-research/api/v1/query` | Run the research workflow |

### `POST /query`

```jsonc
// request
{ "query": "Latest trends in retrieval-augmented generation." }

// response
{ "report": "# Research report\n\n..." }
```

Requires an `OPENAI_API_KEY` (Agents SDK + web search). Without it — or without
the agent dependencies installed — the endpoint returns `503
research_unavailable`, so the hub stays demonstrable when this service is not
configured.

## Architecture

```text
src/backend/
├─ __main__.py                  # app factory (get_app) + lifespan + uvicorn
├─ ai/                          # the multi-agent core (vendored project code)
│  ├─ research_manager.py       #   orchestrates plan → search → write
│  ├─ planner_agent.py          #   decides which searches to run
│  ├─ search_agent.py           #   performs a single web search
│  └─ writer_agent.py           #   writes the final report
└─ webserver/
   ├─ __init__.py               # facade: get_configs / get_logger / Configs
   ├─ configs/configs.py        # Pydantic config
   ├─ configurations.py         # env-driven loader
   ├─ dependency/deps.py        # DI
   ├─ errors.py                 # domain errors + HTTP envelope
   ├─ models/query.py           # request/response models
   ├─ routers/                  # alive · health · status · query
   └─ services/research_service.py  # lazy-runs the agent workflow
```

The workflow is imported and run **lazily** on the first query, so the app and
its probe tests import without the agent stack.

## Run

```bash
uv sync
uv run pytest -q                 # probe tests (no key, no cost)
OPENAI_API_KEY=sk-... uv run python -m backend   # http://localhost:5002/ping
```
