"""Business logic for text analysis."""

from backend.ai.providers.base import LLMProvider
from backend.webserver import Configs, get_logger
from backend.webserver.errors import EmptyTextError, ProviderFailedError
from backend.webserver.models.analyze import AnalysisResult

logger = get_logger(__name__)


class AnalysisService:
    """Coordinates input validation and provider invocation.

    The service is intentionally thin: it validates the request, delegates to
    the injected :class:`LLMProvider`, and normalises any provider failure into
    a domain error. It knows nothing about HTTP or about which concrete
    provider is wired in.
    """

    def __init__(self, configs: Configs, provider: LLMProvider) -> None:
        """Binds the service to its configuration and provider.

        Args:
            configs: Active service configuration.
            provider: Concrete LLM provider selected by the DI layer.
        """
        self._configs = configs
        self._provider = provider

    async def analyze(self, text: str) -> AnalysisResult:
        """Validates and analyses ``text``.

        Args:
            text: Raw text supplied by the caller.

        Returns:
            The structured :class:`AnalysisResult`.

        Raises:
            EmptyTextError: If ``text`` is empty or whitespace only.
            ProviderFailedError: If the provider call raises.
        """
        if not text.strip():
            raise EmptyTextError

        try:
            return await self._provider.analyze(text)
        except Exception as exc:  # noqa: BLE001 - normalised into a domain error
            logger.exception("Provider '%s' failed", self._configs.provider.name)
            raise ProviderFailedError from exc
