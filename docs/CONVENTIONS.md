# Conventions

Every service in this hub follows the same layout and the same rules. Consistency
is intentional: any service can be read, run and reasoned about the same way.

## Service layout

```text
<service>/
  src/backend/
    webserver/                 # the FastAPI application
      __main__.py              #   app factory (get_app) + lifespan + uvicorn
      configs/configs.py       #   Pydantic settings models
      configurations.py        #   env-driven, cached settings loader
      __init__.py              #   facade: get_configs / get_logger / Configs
      routers/                 #   API endpoints (alive · health · status · …)
      services/                #   business logic
      models/                  #   Pydantic request/response models
      dependency/deps.py       #   FastAPI dependency wiring (DI)
      errors.py                #   domain errors → HTTP envelope
    ai/ | job/ | polling/      # optional: AI cores / async workers
    common/connectors/         # optional: storage / external clients
  test/                        # pytest suite
  pyproject.toml · Dockerfile · readme.md
```

## Rules

1. **App factory.** `get_app()` builds the `FastAPI` instance, registers routers,
   error handlers and middleware. A `lifespan` hook logs startup/shutdown. The
   module is runnable with `python -m backend`.
2. **Operational probes.** `GET /ping` at the root; `GET /{prefix}/health` and
   `GET /{prefix}/status` under the API prefix.
3. **Layering.** `router → service → (provider | connector | ai core)`. Routers
   handle HTTP only; services hold logic; the `ai/` layer holds models/agents.
4. **Dependency injection.** Routers depend on factories in `dependency/deps.py`,
   never on concrete implementations — swapping a backend is a config change.
5. **Domain errors.** Business code raises typed exceptions; a single handler in
   `errors.py` maps them to a stable JSON envelope:
   `{"error_code": "...", "message": "...", ...}`.
6. **Lazy heavy imports.** Expensive AI/ML imports happen inside the call path,
   not at module load, so the app and its probe tests import without the heavy
   stack and degrade to `503` when unconfigured.
7. **Config as code.** All settings come from the environment via
   `configurations.py` (cached); no scattered `os.getenv` calls.
8. **uv everywhere.** Each service is managed with `uv` and a committed
   `uv.lock` (where the dependency tree is light enough to lock reliably).

## Naming

* Package root is always `backend`; imports are absolute (`from backend...`).
* API prefix is `/{service-name}/api/v1`.
* Vendored project code lives under `ai/` with imports rewritten to `backend.ai.*`.

## Testing

* Probe tests exercise the microservice surface (app factory, routers, config)
  without the heavy stack — they run anywhere at zero cost.
* Functional tests that need a real model are opt-in and require an API key.
