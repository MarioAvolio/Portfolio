from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings

MODEL = "gpt-4.1-nano"
KNOWLEDGE_BASE=str(Path(__file__).parent.parent.parent / "assets" / "knowledge-base")
DB_NAME=str(Path(__file__).parent.parent.parent / "assets" /  "vector_db")
print(DB_NAME)
EMBEDDINGS = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")