# market-sentinel

Multi-agent competitive intelligence microservice.

**Port:** 5003 | **API prefix:** `/market-sentinel/api/v1`

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/market-sentinel/api/v1/research` | Submit a new competitive analysis job (202 + full `JobRecord`) |
| GET | `/market-sentinel/api/v1/research/jobs/{job_id}` | Poll job status and retrieve report |
| GET | `/market-sentinel/api/v1/research/history` | List recent completed reports from SQLite |
| GET | `/market-sentinel/api/v1/health` | Service health |
| GET | `/market-sentinel/api/v1/ready` | Readiness probe |
| GET | `/market-sentinel/api/v1/status` | Service metadata (name, version, environment) |
| GET | `/ping` | Liveness probe (root, no prefix) |

## Request flow

```mermaid
sequenceDiagram
    participant Client
    participant API as POST /research
    participant Svc as SentinelService
    participant JS as JobStore
    participant Crew as SentinelCrew
    participant RS as ReportStore

    Client->>API: product + competitors
    API->>Svc: submit()
    Svc->>JS: create job (pending)
    Svc-->>Client: 202 + job_id

    Note over Svc,Crew: Background task
    Svc->>JS: status = running
    Svc->>Crew: asyncio.to_thread(run)
    Crew->>Crew: research_task -> analysis_task
    Crew-->>Svc: markdown report
    Svc->>JS: set_result(report)
    Svc->>RS: save(job_id, product, competitors, report)
    Svc->>JS: status = done

    loop Polling
        Client->>API: GET /research/jobs/{job_id}
        API-->>Client: JobRecord (status, report if done)
    end
```

## Env vars

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | LLM for CrewAI agents |
| `SERPER_API_KEY` | Yes | — | Web search via SerperDev |
| `ENVIRONMENT` | No | `local` | Config profile (`local` / `production`) |

## Quick start

```bash
# From repo root
cd services/market-sentinel
uv sync
export OPENAI_API_KEY=sk-...
export SERPER_API_KEY=...
uv run python -m market_sentinel
```

## Testing

```bash
# From services/market-sentinel
uv run pytest test/ -v --cov=src/ --cov-report=term-missing
```

Probe tests run without any API key.
