# Project: AI Microservices Hub (Primary Portfolio Project)

## Overview
A production-style microservices hub where a single API gateway fronts a set of
independent generative-AI services. Each service is self-contained with its own
environment, dependencies, tests, and container.

## Architecture
- Gateway (port 8000): service registry, health aggregation, query routing via httpx
- portfolio-assistant (port 5001): RAG chatbot over a local knowledge base (LangChain + ChromaDB)
- deep-research (port 5002): multi-agent web research producing a markdown report
- market-sentinel (port 5003): multi-agent competitive intelligence (CrewAI) producing a SWOT report

## Technologies
Python, FastAPI, LangChain, ChromaDB, OpenAI Agents SDK, CrewAI, Docker, Docker Compose,
GitHub Actions, pytest, uv, ruff, mypy

## Key Design Decisions
- Services communicate only through the gateway routing API; no direct service-to-service calls
- Lazy ML imports: heavy AI stacks load on first query, keeping probes importable at zero cost
- YAML config files per environment; secrets from env only (no .env files committed)
- Probe tests run at zero cost without an API key; functional tests are opt-in
- Gateway degrades gracefully: unreachable services are listed but do not break the hub

## Repository
github.com/MarioAvolio/Portfolio
