# Mario Avolio — Work in Progress

The following extensions to the AI Microservices Hub are currently in progress:

## Multi-provider LLM Abstraction Layer
Adding support for Gemini and Azure OpenAI alongside the existing OpenAI provider,
behind a unified interface so services can swap providers via config.

## Cloud Deployment Pipeline
Deploying the hub to Google Cloud Run with expanded GitHub Actions CI/CD, enabling
a live public demo beyond local/Docker Compose.

## Dedicated Agentic Tool-Calling Service
A new microservice exposing a structured tool-calling agent (via OpenAI Agents SDK)
as a gateway-routable query endpoint.

## Lakehouse / Observability Layer
Adding a lightweight lakehouse (S3-compatible storage, Parquet, DuckDB) for logging
queries, tracking costs, and enabling analytics over service usage.
