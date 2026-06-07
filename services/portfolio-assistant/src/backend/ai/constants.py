"""Static configuration and resources for the RAG core.

Embeddings are built lazily via :func:`get_embeddings` so importing this module
(and therefore the webserver) stays cheap and free of heavy ML imports until a
query actually needs the pipeline.
"""

from pathlib import Path

MODEL_NAME = "gpt-4.1-nano"

# Project root: .../services/portfolio-assistant  (this file is at src/backend/ai/constants.py)
_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE = str(_ROOT / "assets" / "knowledge-base")
DB_NAME = str(_ROOT / "assets" / "vector_db")


def get_embeddings(backend: str = "openai"):
    """Builds the selected embeddings backend.

    * ``openai`` (default) — ``text-embedding-3-small``: light and fast, no local
      ML stack, a fraction of a cent per build.
    * ``hf`` — local ``all-MiniLM-L6-v2`` via HuggingFace (no API calls, but
      pulls the sentence-transformers / torch stack, installed on demand).

    Args:
        backend: Embeddings backend identifier (``openai`` or ``hf``).

    Returns:
        A LangChain embeddings instance.
    """
    if backend.lower() == "hf":
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(model="text-embedding-3-small")
