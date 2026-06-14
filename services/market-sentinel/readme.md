# market-sentinel

Multi-agent competitive intelligence microservice.

**Port:** 5003 | **API prefix:** `/market-sentinel/api/v1`

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/market-sentinel/api/v1/research` | Submit a new competitive analysis job (returns 202 + job_id) |
| GET | `/market-sentinel/api/v1/research/jobs/{job_id}` | Poll job status and retrieve report |
| GET | `/market-sentinel/api/v1/research/history` | List recent completed reports from SQLite |
| GET | `/market-sentinel/api/v1/health` | Service health |
| GET | `/ping` | Liveness probe |

## Env vars

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | LLM for CrewAI agents |
| `SERPER_API_KEY` | Yes | Web search via SerperDev |

## Quick start

```bash
export OPENAI_API_KEY=sk-...
export SERPER_API_KEY=...
cd services/market-sentinel && uv sync
uv run python -m market_sentinel
```
