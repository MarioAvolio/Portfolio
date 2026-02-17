# 🛡️ InsureLLM Assistant

## 📖 Project Description
**InsureLLM Assistant** is an advanced Generative AI-powered chatbot specifically designed for the insurance domain. It leverages a custom Retrieval-Augmented Generation (RAG) pipeline to ingest, process, and query an internal knowledge base of markdown documents (spanning company policies, contracts, employee data, and insurance products).

Unlike standard out-of-the-box RAG tutorials, this project implements **LLM-assisted Semantic Chunking**, **Dynamic Metadata Tagging**, and **History-Aware Retrieval** to ensure zero hallucinations and deeply contextual, highly accurate answers. 

This project is part of my **AI & Software Engineering Portfolio**, showcasing production-ready patterns for modern LLM applications.

> **💡 Inspiration:** The structural foundation of this project was inspired by [Week 5 of Ed Donner's "LLM Engineering" course](https://github.com/ed-donner/llm_engineering/tree/main/week5), which I significantly adapted to incorporate advanced metadata routing, conversational memory, and AI-driven data processing tailored for the insurance sector.

---

## 🏗️ Advanced RAG Architecture & Features

The pipeline is split into several highly specialized modules, handling everything from data ingestion to conversational querying:

### 1. Document Ingestion & Metadata Tagging (`indexer.py`)
The system parses a structured folder hierarchy of `.md` documents (e.g., `/company`, `/contracts`, `/employees`, `/products`). During the ingestion phase, the `Indexer` automatically injects a `doc_type` metadata tag into every LangChain `Document` based on its parent folder. This ensures that downstream retrieval can always trace the exact origin and category of the information.

### 2. LLM-Powered Semantic Chunking (`splitter.py`)
Instead of relying on naive character or token-based splitting (like standard Recursive Splitters), this project introduces a `CustomTextSplitter`. 
It uses an LLM (`ChatOpenAI`) combined with **Pydantic** (`with_structured_output`) to intelligently parse and structure documents. Every chunk is dynamically reformatted into a strict schema:
- **`headline`**: A brief heading optimized for vector semantic search queries.
- **`summary`**: A generated summary answering common questions about the chunk.
- **`original_text`**: The unedited raw text to ensure strict factual accuracy and prevent data distortion.

### 3. Vector Storage & Retrieval (`indexer.py` & `retriever.py`)
Embeddings are generated and stored inside a local **ChromaDB** vector database. The `Indexer` handles the automatic teardown and rebuild of the vector collections, while the `Retriever` module queries the database returning the top `k=10` most relevant semantic matches based on the user's prompt.

### 4. History-Aware Context Generation (`rag.py`)
To handle follow-up queries fluidly, the `Rag` class dynamically synthesizes the user's conversational history with their latest question. This creates a highly enriched context string that drastically improves the accuracy of the vector similarity search. The retrieved documents are then injected into a dynamically formatted System Prompt before being passed to the LLM for the final answer.

---

## 💻 Tech Stack
- **Language:** Python 3.x
- **Frameworks:** LangChain, Pydantic
- **LLMs & Embeddings:** OpenAI (GPT-4o / GPT-4o-mini)
- **Vector Database:** ChromaDB
- **Package Management:** `uv` / `pyproject.toml`
- **Utilities:** `python-dotenv` (secrets management), `tqdm` (progress tracking)

---

## ⚙️ Installation & Setup

This project uses modern Python packaging with `pyproject.toml` and `uv` for lightning-fast dependency management.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/MarioAvolio/Portfolio.git](https://github.com/MarioAvolio/Portfolio.git)
   cd Portfolio/Insurellm-Assistant

```

2. **Install dependencies:**
If you have [uv]() installed, you can simply sync the environment:
```bash
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

```


*Alternatively, using standard pip:*
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

```


3. **Configure Environment Variables:**
Create a `.env` file in the root of the `Insurellm-Assistant` directory to securely provide your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here

```


4. **Run the Application:**
Execute the main entry point to initialize the ingestion, chunking, and embedding processes, and to trigger a test query ("What is Insurellm?"):
```bash
python src/Insurellm-Assistant/main.py

```



---

## 🚀 Future Roadmap

* **Agentic Routing:** Implement `LangGraph` to route queries dynamically depending on the `doc_type` metadata.
* **Cross-Encoder Reranking:** Add a Cohere or BGE reranker post-retrieval to refine and re-order the top-k documents fetched from ChromaDB.
* **API & UI Layer:** Expose the RAG engine via a **FastAPI** backend and build a conversational frontend using **Streamlit** or **Gradio**.

---
