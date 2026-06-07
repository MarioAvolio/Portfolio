"""Business logic for the deep-research service.

The multi-agent workflow (OpenAI Agents SDK) is imported **lazily** on the first
query, so the app and its probe tests import without the agent stack and the
service degrades gracefully (``503``) when it is not configured.
"""

from deep_research.webserver import Configs, get_logger
from deep_research.webserver.errors import ResearchUnavailableError

logger = get_logger(__name__)


class ResearchService:
    """Runs the multi-agent research workflow for a query."""

    def __init__(self, configs: Configs) -> None:
        """Binds the service to its configuration."""
        self._configs = configs

    async def research(self, query: str) -> str:
        """Runs the workflow and returns the final markdown report.

        The underlying :class:`ResearchManager` streams progress messages and
        yields the markdown report last; only that final value is returned.

        Raises:
            ResearchUnavailableError: If the workflow cannot run (e.g. missing
                API key or dependencies).
        """
        try:
            from deep_research.ai.research_manager import ResearchManager

            report = ""
            async for chunk in ResearchManager().run(query):
                report = chunk  # the final yield is the markdown report
            return report
        except Exception as exc:  # noqa: BLE001 - normalised into a domain error
            logger.exception("Research workflow failed")
            raise ResearchUnavailableError(detail=str(exc)) from exc
