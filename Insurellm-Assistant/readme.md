# InsureLLM Assistant

## Purpose in my portfolio

**InsureLLM Assistant** is a small, end-to-end **Retrieval-Augmented Generation (RAG)** sample aimed at a fictional insurance company. It shows how I structure a Python pipeline—from markdown knowledge sources to vector storage and grounded answers—using patterns that map cleanly to real internal-assistant or document-QA work.

In portfolio terms, it highlights:

- **Domain-shaped data**: Markdown organized by top-level folders (`company`, `contracts`, `employees`, `products`) that mirror how internal docs are often grouped.
- **LLM-assisted chunking**: Documents are split with an OpenAI chat model and **Pydantic structured output** (`headline`, `summary`, `original_text`) so each chunk is easier to retrieve while preserving verbatim source text in `original_text`.
- **Lightweight metadata**: Each chunk carries `doc_type` (from the parent folder) and `source`, which supports traceability and future filtering or routing.
- **History-aware retrieval**: User messages can be folded into the retrieval query and passed through to the final model so follow-ups stay on topic.
- **Local vector store**: Embeddings are computed with **Hugging Face** (`sentence-transformers` / `all-MiniLM-L6-v2`) and stored in **ChromaDB** under `assets/vector_db`, keeping the demo runnable without tying embeddings to a paid API.

This is a **portfolio demonstration**, not a production product: the ingestion path currently caps loaded documents for faster iteration (see `indexer.py`). The design is intentionally clear and modular so the same ideas scale to larger corpora, UI layers, and stricter evaluation.

**Inspiration:** The overall shape of the project builds on ideas from [Week 5 of Ed Donner’s “LLM Engineering” course](https://github.com/ed-donner/llm_engineering/tree/main/week5), extended here with Insurellm-specific prompts, metadata, chunk schema, and retrieval/chat wiring.

---

## How it works (aligned with the code)

| Stage | Module | What it does |
|--------|--------|----------------|
| Load & tag | `indexing/indexer.py` | Walks `assets/knowledge-base/*`, loads `**/*.md` per folder, sets `metadata["doc_type"]` from the folder name. |
| Chunk | `indexing/splitter.py` | `CustomTextSplitter` calls `ChatOpenAI(...).with_structured_output(Chunks)`; each chunk becomes a LangChain `Document` whose `page_content` concatenates headline, summary, and original text. |
| Embed & store | `indexing/indexer.py` | Rebuilds a Chroma collection (deletes existing DB dir content when present), embeds chunks, persists to `assets/vector_db`. |
| Retrieve | `retrieval/retriever.py` | Wraps the vector store as a retriever with `k=10` (see class defaults). |
| Answer | `llm/rag.py` | Builds a **combined** string from prior user turns + latest question for retrieval; formats a system prompt with retrieved context; sends system + optional history + latest user message to the chat model. |

Entry point: `src/Insurellm-Assistant/main.py` loads env vars, runs indexing → retriever → `Rag`, and prints the answer for a sample question (`"What is Insurellm?"`).

Configuration: `src/Insurellm-Assistant/constants.py` sets `KNOWLEDGE_BASE`, `DB_NAME`, `MODEL_NAME` (chat model), and `HuggingFaceEmbeddings` for vectors.

---

## Tech stack (as used in this repo)

- **Python** 3.11+ (`pyproject.toml`)
- **LangChain** (community, Chroma, OpenAI, Hugging Face integrations), **Pydantic**, **ChromaDB**
- **OpenAI** API for chat and structured chunking (`gpt-4.1-nano` in `constants.py` / `splitter.py`)
- **Embeddings:** `langchain_huggingface` + `all-MiniLM-L6-v2`
- **Environment:** `python-dotenv`
- **Progress:** `tqdm` during chunking

`pyproject.toml` lists additional dependencies used elsewhere in the monorepo-style environment; the assistant code path above relies on the stack in this section.

---

## Installation and setup

1. **Clone the repository** (this project lives under the Portfolio repo):

   ```bash
   git clone https://github.com/MarioAvolio/Portfolio.git
   cd Portfolio/Insurellm-Assistant
   ```

2. **Install dependencies**

   With [uv](https://github.com/astral-sh/uv):

   ```bash
   uv sync
   ```

   On Windows, activate the virtual environment:

   ```bash
   .venv\Scripts\activate
   ```

   If you do not use uv, create a virtual environment, activate it, and install what you need from the `[project].dependencies` list in `pyproject.toml` (this repo’s manifest pulls in a broad set of packages; uv keeps that reproducible in one step).

3. **Environment variables**

   Create a `.env` file in the `Insurellm-Assistant` directory:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   Hugging Face embeddings use local `sentence-transformers` weights; ensure you have network access on first run if models need downloading.

4. **Run**

   ```bash
   python src/Insurellm-Assistant/main.py
   ```

   This rebuilds the vector index (for the documents currently loaded in code), runs retrieval, and prints the model’s answer for the sample question.
