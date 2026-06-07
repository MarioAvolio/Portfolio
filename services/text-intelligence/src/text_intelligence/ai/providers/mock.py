"""Deterministic, dependency-free provider.

``MockProvider`` produces a plausible :class:`AnalysisResult` using only simple
heuristics. It needs no API key and no network, which keeps the service
runnable and the test suite green at zero cost. It is the default provider and
the reference implementation real providers are validated against.
"""

import re

from text_intelligence.ai.providers.base import LLMProvider
from text_intelligence.webserver.models.analyze import AnalysisResult, Sentiment

_POSITIVE = {"good", "great", "love", "excellent", "happy", "buono", "ottimo", "bene"}
_NEGATIVE = {"bad", "terrible", "hate", "awful", "sad", "brutto", "male", "pessimo"}
_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "is",
    "it",
    "this",
    "that",
    "il",
    "lo",
    "la",
    "un",
    "una",
    "e",
    "di",
    "che",
    "per",
    "con",
    "del",
}
_WORD = re.compile(r"[A-Za-zÀ-ÿ']+")


class MockProvider(LLMProvider):
    """Heuristic provider used for local runs, CI and as a fallback."""

    def __init__(self, model: str = "mock-1") -> None:
        """Stores the model label echoed back in results.

        Args:
            model: Identifier surfaced as :attr:`AnalysisResult.model`.
        """
        self._model = model

    async def analyze(self, text: str) -> AnalysisResult:
        """Returns a heuristic analysis of ``text``."""
        words = _WORD.findall(text.lower())
        return AnalysisResult(
            summary=self._summarize(text),
            sentiment=self._sentiment(words),
            tags=self._tags(words),
            language=self._language(words),
            model=self._model,
        )

    @staticmethod
    def _summarize(text: str) -> str:
        """First sentence, truncated to a single readable line."""
        first = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)[0]
        return first if len(first) <= 200 else f"{first[:197]}..."

    @staticmethod
    def _sentiment(words: list[str]) -> Sentiment:
        """Net polarity from positive/negative word counts."""
        score = sum(w in _POSITIVE for w in words) - sum(w in _NEGATIVE for w in words)
        if score > 0:
            return "positive"
        if score < 0:
            return "negative"
        return "neutral"

    @staticmethod
    def _tags(words: list[str], limit: int = 5) -> list[str]:
        """Most frequent meaningful words, preserving first-seen order."""
        counts: dict[str, int] = {}
        for word in words:
            if len(word) > 3 and word not in _STOPWORDS:
                counts[word] = counts.get(word, 0) + 1
        ranked = sorted(counts, key=lambda w: counts[w], reverse=True)
        return ranked[:limit]

    @staticmethod
    def _language(words: list[str]) -> str:
        """Naive it/en guess from common function words."""
        it_markers = {"il", "che", "di", "per", "con", "una", "del", "non"}
        return "it" if any(w in it_markers for w in words) else "en"
