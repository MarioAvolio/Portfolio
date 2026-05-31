"""Assembly of the RAG pipeline.

Wires the indexing, retrieval and generation stages into a ready-to-use
:class:`~backend.ai.llm.rag.Rag` instance. This replaces the original
``main.py`` script entrypoint with a reusable factory the webserver calls.

Chunking strategy is configurable:

* ``simple`` (default) — ``RecursiveCharacterTextSplitter``: deterministic and
  free, no LLM calls during indexing.
* ``llm`` — an LLM-assisted splitter that produces richer, summarised chunks at
  the cost of one model call per document.
"""

import os

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.ai.constants import DB_NAME, KNOWLEDGE_BASE, MODEL_NAME, get_embeddings
from backend.ai.indexing.indexer import Indexer
from backend.ai.llm.rag import Rag
from backend.ai.retrieval.retriever import Retriever


def _make_splitter():
    """Builds the chunking strategy selected by ``INSURELLM_CHUNKING``."""
    if os.getenv("INSURELLM_CHUNKING", "simple").lower() == "llm":
        from backend.ai.indexing.splitter import CustomTextSplitter

        return CustomTextSplitter()
    return RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def _max_documents():
    """Optional document cap from ``INSURELLM_MAX_DOCS`` (default: all)."""
    raw = os.getenv("INSURELLM_MAX_DOCS")
    return int(raw) if raw else None


def build_rag() -> Rag:
    """Builds the full RAG pipeline (indexing → retrieval → generation).

    The vector store is persisted and reused across runs; only the answer step
    requires an ``OPENAI_API_KEY``.

    Returns:
        A :class:`Rag` ready to answer questions.
    """
    vector_store = Indexer(
        knowledge_base=KNOWLEDGE_BASE,
        db_name=DB_NAME,
        embeddings=get_embeddings(),
        splitter=_make_splitter(),
        max_documents=_max_documents(),
    ).get_vector_store()
    return Rag(model_name=MODEL_NAME, retriever=Retriever(vector_store))
