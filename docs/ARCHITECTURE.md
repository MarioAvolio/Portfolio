# Architecture

This repository is a **microservices hub**: a single API gateway fronts a set of
independent FastAPI services. Each service is self-contained -- its own
environment, dependencies, tests and container -- and is reachable only through
the gateway's uniform routing API.

## Diagrams

| Diagram | Description |
| --- | --- |
| [Gateway routing flow](diagrams/flow-gateway.svg) | How a client query traverses the gateway to a microservice |
| [Async job pattern](diagrams/flow-async-job.svg) | Fire-and-forget job submission, polling, and background execution |
| [RAG pipeline](diagrams/flow-rag.svg) | Retrieval-Augmented Generation inside portfolio-assistant |

## Components

| Component | Port | Role |
| --- | --- | --- |
| `gateway` | 8000 | Service registry, health aggregation, query routing |
| `portfolio-assistant` | 5001 | RAG chatbot over Mario Avolio's professional profile |
| `deep-research` | 5002 | Multi-agent web research producing a markdown report |
| `market-sentinel` | 5003 | Competitive intelligence SWOT via CrewAI + SQLite |

## Topology

```text
                       +----------------------------------------+
   client ------------> |  gateway                                |
                        |  GET  /services                         |  registry + health
                        |  POST /services/{name}/query            |  routes over HTTP
                        |  GET  /services/{name}/jobs/{job_id}     |  poll async jobs
                        |  GET  /audit                             |  recent routed calls
                        +-------------+----------------------------+
                                      |  httpx
              +-------------------+---+---------------------+
              |                   |                         |
              v                   v                         v
     portfolio-assistant      deep-research           market-sentinel
     RAG chatbot              async job research       SWOT intelligence
```

## Request flow (routed query)

1. Client calls `POST /gateway/api/v1/services/{name}/query` with a JSON body.
2. The gateway looks the service up in its registry (404 if unknown).
3. It forwards the body **verbatim** to the service's `query_path` over HTTP.
4. The downstream response and status code are relayed back to the client.
5. If the service is unreachable, the gateway returns `503 service_unavailable`.

The gateway never interprets a service's payload schema, so services evolve
independently. Each service documents its own request shape, surfaced in the
`query_example` field of `GET /services`.

## Console

The gateway serves a static web console at `http://localhost:8000/ui/`.
It lists registered services with live health, lets you send a query to any
(service's `query_example`), and automatically polls async jobs by their
`job_id` until completion, showing status transitions (pending -> running -> done).
It is a thin read-oriented client with no business logic and no auth (local demo only).

## Async job pattern (deep-research, market-sentinel)

Some services use a two-step async job API rather than a synchronous response:

1. `POST /{service}/api/v1/research` -- submit work, returns `202 Accepted` with `job_id`.
2. `GET /{service}/api/v1/research/jobs/{job_id}` -- poll until `status` is `done` or `failed`.

market-sentinel adds a third endpoint: `GET /market-sentinel/api/v1/research/history`
returning recent completed reports from SQLite.

The gateway provides a unified polling entrypoint: `GET /gateway/api/v1/services/{name}/jobs/{job_id}`
which relays the downstream job document verbatim (same schema-agnostic pattern
as existing `POST /services/{name}/query`).

## Audit trail

Every routed call already passes through the gateway, which makes it the
natural place to keep a compact record of recent activity: `GET
/gateway/api/v1/audit?limit=N` returns the last N calls (service, kind,
status code, latency, timestamp), newest first. The record is written
in-process to a bounded in-memory ring buffer -- no queue, no external
store -- because it costs nothing to lose and nothing to regenerate at this
scale, and it must not add latency to the call it describes. History resets
on restart; a durable version is planned as part of the Cloud storage
roadmap step, not missing by accident.

## Health model

Every service exposes the same operational trio:

* `GET /ping` -- liveness, mounted at the root for container/orchestration probes.
* `GET /{prefix}/health` -- health check.
* `GET /{prefix}/status` -- identifying metadata (name, version, environment).

`GET /gateway/api/v1/services` aggregates the liveness of all registered
services concurrently and reports each as `healthy` or `unreachable`.

## Cost and degradation

`gateway` runs at ~$0 (no API key needed). `portfolio-assistant` and
`deep-research` perform real model calls and require `OPENAI_API_KEY`; without
it their `/query` returns `503` while their probes keep working -- the hub stays
demonstrable end to end. `market-sentinel` also requires `OPENAI_API_KEY`
and `SERPER_API_KEY`.

The same request id appears in the gateway's log, the audit trail, and each downstream service's own log for one end-to-end call, because every service already runs the same request-id middleware and adopts an inbound id instead of generating its own; retries are scoped to connection failures only, so a paid model call is never fired twice for one slow response, and each attempt shows as its own row in the audit trail.

## Configuration

Each service loads non-secret settings from a YAML file
(`webserver/configs/files/<env>.yml`, selected by `ENVIRONMENT`), overlaid on
Pydantic defaults and cached in `webserver/configurations.py`. No `.env` file is
used; secrets (API keys) come from the environment only. The gateway registry is
declared in its YAML, and each downstream `base_url` is overridable via a
`*_URL` environment variable, derived from the service name (`PORTFOLIO_ASSISTANT_URL`,
`DEEP_RESEARCH_URL`, `MARKET_SENTINEL_URL`) -- how docker-compose points at
in-network hostnames.

See [CONVENTIONS.md](CONVENTIONS.md) for the service layout and [RUNBOOK.md](RUNBOOK.md)
for how to run and test everything.
