# syntax=docker/dockerfile:1
# NOTE: this image is heavy (OpenAI Agents SDK, LangGraph, AutoGen, Playwright,
# ...). It is not built by the default `docker compose up`; build it explicitly
# when you want to run the research service with an OPENAI_API_KEY.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PORT=5002

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

EXPOSE 5002

CMD ["uv", "run", "--no-sync", "uvicorn", "backend.__main__:get_app", "--factory", "--host", "0.0.0.0", "--port", "5002"]
