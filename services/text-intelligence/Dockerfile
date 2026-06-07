# syntax=docker/dockerfile:1
FROM python:3.12-slim

# uv: fast, reproducible environment manager (pinned binary from the official image).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PORT=5000

WORKDIR /app

# Install dependencies first (cached) using the lockfile, without dev tools.
COPY pyproject.toml uv.lock readme.md ./
RUN uv sync --frozen --no-dev --no-install-project

# Then add the application source and install the project itself.
COPY src ./src
RUN uv sync --frozen --no-dev

EXPOSE 5000

# Serve the app factory through uvicorn inside the uv-managed environment.
CMD ["uv", "run", "--no-sync", "uvicorn", "backend.__main__:get_app", "--factory", "--host", "0.0.0.0", "--port", "5000"]
