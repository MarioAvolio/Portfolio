"""Assembly of the RAG pipeline.

Wires the indexing, retrieval and generation stages into a ready-to-use
:class:`~backend.ai.llm.rag.Rag` instance. This replaces the original
``main.py`` script entrypoint with a reusable factory the webserver calls,
driven entirely by the service configuration.

Chunking strategy (``rag.chunking``):

* ``simple`` (default) — ``RecursiveCharacterTextSplitter``: deterministic and
  free, no LLM calls during indexing.
* ``llm`` — an LLM-assisted splitter that produces richer, summarised chunks at
  the cost of one model call per document.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.ai.constants import DB_NAME, KNOWLEDGE_BASE, get_embeddings
from backend.ai.indexing.indexer import Indexer
from backend.ai.llm.rag import Rag
from backend.ai.retrieval.retriever import Retriever


def _make_splitter(chunking: str):
    """Builds the chunking strategy named by ``chunking``."""
    if chunking.lower() == "llm":
        from backend.ai.indexing.splitter import CustomTextSplitter

        return CustomTextSplitter()
    return RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def build_rag(configs) -> Rag:
    """Builds the full RAG pipeline (indexing → retrieval → generation).

    The vector store is persisted and reused across runs; only the answer step
    (and OpenAI embeddings, when selected) require an ``OPENAI_API_KEY``.

    Args:
        configs: The service configuration carrying the ``rag`` block and the
            chat ``model_name``.

    Returns:
        A :class:`Rag` ready to answer questions.
    """
    rag = configs.rag
    vector_store = Indexer(
        knowledge_base=KNOWLEDGE_BASE,
        db_name=DB_NAME,
        embeddings=get_embeddings(rag.embeddings),
        splitter=_make_splitter(rag.chunking),
        max_documents=rag.max_documents,
    ).get_vector_store()
    return Rag(model_name=configs.model_name, retriever=Retriever(vector_store))
