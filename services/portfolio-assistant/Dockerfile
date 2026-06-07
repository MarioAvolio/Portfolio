# syntax=docker/dockerfile:1
# NOTE: this image is heavy (LangChain, torch, transformers, ...). It is not
# built by the default `docker compose up`; build it explicitly when you want to
# run the RAG service with an OPENAI_API_KEY.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PORT=5001

WORKDIR /app

COPY pyproject.toml uv.lock readme.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY assets ./assets
RUN uv sync --frozen --no-dev

EXPOSE 5001

CMD ["uv", "run", "--no-sync", "uvicorn", "portfolio_assistant.__main__:get_app", "--factory", "--host", "0.0.0.0", "--port", "5001"]
