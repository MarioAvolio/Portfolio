"""Provider abstraction for text analysis.

The :class:`LLMProvider` interface is the single extension point through which
new backends (mock, Gemini, OpenAI, Azure OpenAI ...) plug into the service.
The webserver layer depends only on this contract, never on a concrete
implementation, so adding a provider never touches the routing or service code.
"""

from abc import ABC, abstractmethod

from text_intelligence.webserver.models.analyze import AnalysisResult


class LLMProvider(ABC):
    """Contract every text-analysis backend must satisfy."""

    @abstractmethod
    async def analyze(self, text: str) -> AnalysisResult:
        """Analyses ``text`` and returns a structured result.

        Args:
            text: Free-form input text, guaranteed non-empty by the caller.

        Returns:
            A populated :class:`AnalysisResult`.

        Raises:
            Exception: Implementation-specific transport or model failures.
                The service layer translates these into a domain error.
        """
        raise NotImplementedError
