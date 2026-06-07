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
      configs/__init__.py      #   env anchors (ENVIRONMENT → CONFIG_FILE)
      configs/files/local.yml  #   non-secret config overrides per environment
      configurations.py        #   cached loader: defaults ← YAML overlay
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
   module is runnable with \`python -m <package>\` (e.g. \`gateway\`, \`text_intelligence\`,
   \`portfolio_assistant\`, \`deep_research\`).
2. **Operational probes.** `GET /ping` at the root (no prefix); `GET /{prefix}/health`,
   `GET /{prefix}/ready`, and `GET /{prefix}/status` under the API prefix.
   All four must be covered by zero-cost probe tests.
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
7. **Config from YAML, not `.env`.** Non-secret settings live in
   `configs/files/<env>.yml`. `configs/__init__.py` resolves the active
   environment (`ENVIRONMENT`, default `local`) to a config file; in deployment
   any non-local environment reads `/app/settings/config.yaml` (e.g. a mounted
   configmap). `configurations.py` overlays that YAML on the Pydantic defaults
   and caches the result. **Secrets** (API keys) are read from the environment
   only — never from YAML, never from a committed `.env`.
8. **uv everywhere.** Each service has its own `pyproject.toml` and `uv.lock`.
   A root `pyproject.toml` declares a uv workspace (`[tool.uv.workspace]`) so
   `uv sync` at the repo root installs all services into a single shared `.venv`.
9. **Docstrings.** Every public function, method and class must have a
   Google-style docstring (`Args:`, `Returns:`, `Raises:` sections). One-liners
   with no parameters are fine as-is. No comments unless the WHY is non-obvious.
10. **Dockerfile.** Copy `readme.md` (or `README.md`) alongside `pyproject.toml`
    and `uv.lock` before the first `RUN uv sync` step — hatchling requires the
    readme to build the package metadata.

## Naming

* Each service exposes a unique Python package: \`gateway\`, \`text_intelligence\`,
  \`portfolio_assistant\`, \`deep_research\`. Imports are absolute (\`from gateway...\`).
* API prefix is `/{service-name}/api/v1`.
* Vendored project code lives under \`ai/\` with imports rewritten to the service package
  (e.g. \`from gateway.ai.*\`).

## Testing

* Probe tests exercise the microservice surface (app factory, routers, config)
  without the heavy stack — they run anywhere at zero cost.
* Functional tests that need a real model are opt-in and require an API key.
