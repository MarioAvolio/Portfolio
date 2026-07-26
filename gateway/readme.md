# gateway

Single entrypoint of the **[Portfolio microservices hub](../readme.md)**. A
FastAPI service that holds a **registry** of downstream microservices, aggregates
their health, and **routes queries** to them over HTTP.

It is a thin reverse proxy: it forwards each request body verbatim to the target
service and relays the response, so it stays fully decoupled from every
service's payload schema, implementing a classic API-gateway / service-registry
pattern.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/ping` | Liveness probe |
| `GET` | `/gateway/api/v1/health` | Health check |
| `GET` | `/gateway/api/v1/status` | Gateway metadata + registered services |
| `GET` | `/gateway/api/v1/services` | List services with live health |
| `POST` | `/gateway/api/v1/services/{name}/query` | Route a query to a service |
| `GET` | `/gateway/api/v1/services/{name}/jobs/{job_id}` | Poll an async job on a service |
| `GET` | `/gateway/api/v1/audit` | Recent routed calls (newest first) |

### Routing a query

```bash
# unified entrypoint -> queries a service
curl -X POST localhost:8000/gateway/api/v1/services/portfolio-assistant/query \
  -H 'content-type: application/json' \
  -d '{"question": "What technologies does Mario know?"}'
```

The body is forwarded as-is; each service documents its own schema (surfaced in
`query_example` by `GET /services`). If a service is down or unconfigured the
gateway returns `503 service_unavailable` -- it degrades gracefully.

### Console

The gateway serves a static web console at `http://localhost:8000/ui/`.
It lists registered services with live health, lets you send a query to any
service (prefilled from its `query_example`), and automatically polls async
jobs by their `job_id` until completion, showing status transitions
(pending -> running -> done). The console also shows a "Recent activity"
panel displaying the last 20 routed calls.
It is a thin read-oriented client with no business logic and no auth (local demo only).

## Request flow

Every routed call carries `X-Request-ID` onward to the downstream service, using the same header name the gateway's own middleware reads on the way in.

```mermaid
sequenceDiagram
    participant Client
    participant GW as Gateway
    participant Reg as Service Registry
    participant DS as Downstream Service

    Client->>GW: POST /services/{name}/query
    GW->>Reg: lookup(name)
    alt name unknown
        Reg-->>GW: not found
        GW-->>Client: 404 service_not_found
    end
    Reg-->>GW: base_url, query_path

    GW->>DS: POST {base_url}{query_path} (body forwarded verbatim)
    alt service unreachable / timeout
        DS-->>GW: connection error
        GW-->>Client: 503 service_unavailable
    end
    DS-->>GW: response (any status)
    GW-->>Client: relay response

    Note over GW,Reg: GET /services aggregates health<br/>of all registered services concurrently

    alt client polls async jobs
        Client->>GW: GET /services/{name}/jobs/{job_id}
        GW->>DS: relay to /jobs/{job_id} (schema-agnostic)
        DS-->>GW: job status
        GW-->>Client: relay response
    end
```

## Registry

Services are declared in [`configs/files/local.yml`](src/gateway/webserver/configs/files/local.yml)
(name, description, paths, example body, default `base_url`). Each base URL is
overridable with a `*_URL` environment variable, derived from the service name
(e.g. `PORTFOLIO_ASSISTANT_URL`, `DEEP_RESEARCH_URL`, `MARKET_SENTINEL_URL`) --
used by docker-compose to point at the in-network service hostnames.
`request_timeout_seconds` (in the YAML) bounds each downstream call. Async
services also declare an optional `job_path` (e.g.
`/deep-research/api/v1/research/jobs`) for polling background jobs.

`retry_attempts` (default 2, meaning one retry) and `retry_delay_seconds`
(default 0.2) control retrying a connection failure. Only a connection failure is
retried -- a slow response that already reached the service (a read timeout)
is deliberately NOT retried, because that request may already be running a
paid model call downstream, and firing a second one would be worse than the
delay it would paper over.

## Audit trail

`GET /gateway/api/v1/audit?limit=N` returns the most recently routed calls,
newest first: service, kind (`query` or `job_status`), status code, latency
in ms, timestamp, request id. It only records calls that actually reached a
downstream service -- unknown-service calls and health probes are not
recorded. Storage is a bounded in-memory ring buffer (`audit_capacity` in
the YAML, default 200); it resets on every restart by design.

## Run

```bash
uv sync
uv run pytest -q
uv run python -m gateway          # http://localhost:8000/ping
```

The whole hub (gateway + services) is orchestrated from the
[root `docker-compose.yml`](../docker-compose.yml).
