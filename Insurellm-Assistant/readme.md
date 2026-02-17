# 🛡️ InsureLLM Assistant

## 📖 Project Description
**InsureLLM Assistant** is a Generative AI-powered assistant designed specifically for the insurance sector. It allows users to upload, analyze, and query complex insurance documents (such as policies, terms and conditions, and claim guidelines), delivering highly accurate and context-aware answers in natural language.

This project is part of my **Agentic & Generative AI** portfolio, demonstrating the practical application of advanced Natural Language Processing (NLP) architectures to solve real-world industry challenges.

> **💡 Inspiration & Credits:** > The core architecture of this project is based on the concepts covered in [Week 5 of Ed Donner's "LLM Engineering" repository](https://github.com/ed-donner/llm_engineering/tree/main/week5), which focuses on advanced RAG (Retrieval-Augmented Generation) pipelines. I adapted and extended these principles to tackle a complex use case within the *Insurance* domain.

## 🎯 Goals
Insurance documents are notoriously lengthy, highly technical, and difficult to navigate. **InsureLLM** aims to break down this cognitive barrier using AI:

* **Zero Hallucinations:** By leveraging a strict RAG approach, the LLM generates answers **exclusively** based on the clauses and text provided in the uploaded documents.
* **Instant Semantic Search:** Retrieves the most relevant paragraphs in fractions of a second, going far beyond the limitations of traditional keyword search.
* **Conversational Experience:** The assistant maintains conversational memory to handle follow-up questions effectively (e.g., "What happens if the accident occurs abroad instead?").

## 🛠️ Features & Architecture (RAG Pipeline)
1.  **Document Ingestion & Text Splitting:** Parses insurance PDFs and splits them into optimal semantic chunks using LangChain.
2.  **Embeddings & Vector Store:** Converts text chunks into vector embeddings and stores them in a Vector Database (e.g., ChromaDB / FAISS) for high-speed retrieval.
3.  **Retrieval Chain:** Upon receiving a user query, the system performs a similarity search to fetch the most semantically relevant text fragments.
4.  **Generation:** A Large Language Model (LLM) synthesizes the retrieved context into a clear, concise, and accurate response.

## 💻 Tech Stack
* **Language:** Python 3.x
* **AI Framework:** LangChain
* **LLM / Embeddings:** OpenAI / Llama 3 (or other open-source alternatives)
* **Vector Database:** ChromaDB / FAISS

## ⚙️ Installation & Setup

1.  **Clone the repository and navigate to the project folder:**
    ```bash
    git clone [https://github.com/MarioAvolio/Portfolio.git](https://github.com/MarioAvolio/Portfolio.git)
    cd Portfolio/Insurellm-Assistant
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the root directory to safely store your API keys:
    ```env
    OPENAI_API_KEY=your_api_key_here
    ```

4.  **Execution:**
    * First, run the ingestion script (or Notebook cell) to process your test documents (place your sample policy PDFs in the designated `data` folder).
    * Next, launch the interactive script to start querying the **Assistant**.

## 🚀 Future Enhancements
* **Multi-Document Comparison:** Integrate Agentic AI workflows (e.g., LangGraph) to compare coverages and deductibles across two different policies.
* **Reranking:** Implement a Cross-Encoder reranking node to boost the precision of vector retrieval.
* **Backend Integration:** Expose the assistant via a RESTful API using **FastAPI**.

## 👨‍💻 Author
**Mario Avolio** - AI & Software Engineer  
Specialized in Computer Vision, Gen/Agentic AI, Model Optimization, and Backend Infrastructure.  
[GitHub Profile](https://github.com/MarioAvolio)
