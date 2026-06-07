# Architecture

This repository is a **microservices hub**: a single API gateway fronts a set of
independent FastAPI services. Each service is self-contained — its own
environment, dependencies, tests and container — and is reachable only through
the gateway's uniform routing API.

## Components

| Component | Port | Role |
| --- | --- | --- |
| `gateway` | 8000 | Service registry, health aggregation, query routing |
| `text-intelligence` | 5000 | Structured text analysis over a pluggable LLM provider |
| `portfolio-assistant` | 5001 | RAG chatbot over Mario Avolio's professional profile |
| `deep-research` | 5002 | Multi-agent web research producing a markdown report (async job via POST /research, poll via GET /research/jobs/{id}) |

## Topology

```text
                       ┌────────────────────────────┐
   client ───────────► │  gateway                   │
                       │  GET  /services            │  registry + health
                       │  POST /services/{name}/query  routes over HTTP
                       └──────────────┬─────────────┘
                                      │ httpx
            ┌─────────────────────────┼──────────────────────────┐
            ▼                         ▼                          ▼
    text-intelligence            portfolio-assistant                  deep-research
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

## Health model

Every service exposes the same operational trio:

* `GET /ping` — liveness, mounted at the root for container/orchestration probes.
* `GET /{prefix}/health` — health check.
* `GET /{prefix}/status` — identifying metadata (name, version, environment).

`GET /gateway/api/v1/services` aggregates the liveness of all registered
services concurrently and reports each as `healthy` or `unreachable`.

## Cost & degradation

The default path runs at ~$0: `gateway` and `text-intelligence` need no API key
(the latter defaults to a deterministic mock provider). `portfolio-assistant` and
`deep-research` perform real model calls and require an `OPENAI_API_KEY`; without
it their `/query` returns `503` while their probes keep working — the hub stays
demonstrable end to end.

## Configuration

Each service loads non-secret settings from a YAML file
(`webserver/configs/files/<env>.yml`, selected by `ENVIRONMENT`), overlaid on
Pydantic defaults and cached in `webserver/configurations.py`. No `.env` file is
used; secrets (API keys) come from the environment only. The gateway registry is
declared in its YAML, and each downstream `base_url` is still overridable via a
`*_URL` environment variable (`TEXT_INTELLIGENCE_URL`, `INSURELLM_URL`,
`DEEP_RESEARCH_URL`) — how docker-compose points it at in-network hostnames.

See [CONVENTIONS.md](CONVENTIONS.md) for the service layout and [RUNBOOK.md](RUNBOOK.md)
for how to run and test everything.
