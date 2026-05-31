"""Environment-driven loader for the gateway configuration and registry.

The registry defaults to docker-compose service URLs so ``docker compose up``
wires everything automatically. Each base URL is overridable via an environment
variable (``TEXT_INTELLIGENCE_URL`` and so on) for local or cloud runs.
"""

import os
from functools import lru_cache

from .configs.configs import Configs, ServiceEndpoint


def _registry() -> list[ServiceEndpoint]:
    """Builds the downstream service registry from environment overrides."""
    return [
        ServiceEndpoint(
            name="text-intelligence",
            description="Structured text analysis (summary, sentiment, tags, language).",
            base_url=os.getenv("TEXT_INTELLIGENCE_URL", "http://text-intelligence:5000"),
            query_path="/text-intelligence/api/v1/analyze",
            query_example={"text": "I love this great product."},
        ),
        ServiceEndpoint(
            name="insurellm",
            description="RAG assistant over the InsureLLM knowledge base.",
            base_url=os.getenv("INSURELLM_URL", "http://insurellm:5001"),
            query_path="/insurellm/api/v1/query",
            query_example={"question": "What is Insurellm?"},
        ),
        ServiceEndpoint(
            name="deep-research",
            description="Multi-agent web research producing a structured report.",
            base_url=os.getenv("DEEP_RESEARCH_URL", "http://deep-research:5002"),
            query_path="/deep-research/api/v1/query",
            query_example={"query": "Latest trends in retrieval-augmented generation."},
        ),
    ]


@lru_cache
def get_configs() -> Configs:
    """Builds the cached gateway configuration from the environment.

    Returns:
        The process-wide :class:`Configs` singleton.
    """
    return Configs(
        environment=os.getenv("ENVIRONMENT", "local"),
        api_prefix=os.getenv("API_PREFIX", "/gateway/api/v1"),
        request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60")),
        services=_registry(),
    )
