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


def get_llm(provider: str = "openai", model_name: str = "gpt-4.1-nano"):
    """Builds the selected LLM backend.

    Reads secrets from environment variables only (never from config):
    * ``openai``  -- reads ``OPENAI_API_KEY``
    * ``google``  -- reads ``GOOGLE_API_KEY`` (Google AI Studio key, not GCP)
    * ``hf``      -- reads ``HF_TOKEN``; uses HF Inference Router (OpenAI-compatible)
    * ``ollama``  -- no key needed; requires Ollama running at ``OLLAMA_BASE_URL``
                     (default: http://localhost:11434)

    Args:
        provider: LLM backend identifier (``openai``, ``google``, ``hf``, or ``ollama``).
        model_name: Model identifier passed to the selected backend.

    Returns:
        A LangChain chat model instance.

    Raises:
        ValueError: If ``provider`` is not a recognised value.
    """
    if provider == "google":
        import os
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0)

    if provider == "hf":
        import os
        from langchain_openai import ChatOpenAI

        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        return ChatOpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=token,
            model=model_name,
            temperature=0.1,
            max_tokens=512,
        )

    if provider == "ollama":
        import os
        from langchain_ollama import ChatOllama

        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model_name, base_url=base_url, temperature=0.1)

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(temperature=0, model_name=model_name)

    raise ValueError(f"Unknown LLM provider: {provider!r}. Choose openai | google | hf | ollama.")


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
