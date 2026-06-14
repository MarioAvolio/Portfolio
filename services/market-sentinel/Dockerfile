FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml .
COPY readme.md .
COPY src/ ./src/

RUN uv sync --no-dev

EXPOSE 5003

CMD ["uv", "run", "python", "-m", "market_sentinel"]
