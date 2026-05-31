"""Business logic for the insurellm RAG service.

The heavyweight RAG pipeline (LangChain, Chroma, embeddings, OpenAI) is imported
and built **lazily** on the first query and cached thereafter. This keeps the
app — and the probe tests — importable without the ML stack, and lets the
service degrade gracefully (``503``) when it is not configured.
"""

from backend.webserver import Configs, get_logger
from backend.webserver.errors import RagUnavailableError

logger = get_logger(__name__)


class RagService:
    """Answers questions against the InsureLLM knowledge base."""

    _rag = None  # cached pipeline, built on first use

    def __init__(self, configs: Configs) -> None:
        """Binds the service to its configuration."""
        self._configs = configs

    def _pipeline(self):
        """Lazily builds and caches the RAG pipeline.

        Raises:
            RagUnavailableError: If the pipeline cannot be built.
        """
        if RagService._rag is None:
            try:
                from backend.ai.pipeline import build_rag

                RagService._rag = build_rag(self._configs)
            except Exception as exc:  # noqa: BLE001 - normalised into a domain error
                logger.exception("Failed to build the RAG pipeline")
                raise RagUnavailableError(detail=str(exc)) from exc
        return RagService._rag

    def answer(self, question: str) -> tuple[str, list[str]]:
        """Answers ``question`` and returns the answer plus its sources.

        Raises:
            RagUnavailableError: If the pipeline cannot be built or queried.
        """
        try:
            answer, docs = self._pipeline().answer_question(question)
        except RagUnavailableError:
            raise
        except Exception as exc:  # noqa: BLE001 - normalised into a domain error
            logger.exception("RAG query failed")
            raise RagUnavailableError(detail=str(exc)) from exc
        sources = [doc.metadata.get("source", "") for doc in docs]
        return answer, sources
