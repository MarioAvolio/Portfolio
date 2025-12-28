from indexing.indexer import Indexer
from constants import DB_NAME, EMBEDDINGS, KNOWLEDGE_BASE, MODEL_NAME
from retrieval.retriever import Retriever
from llm.rag import Rag
from dotenv import load_dotenv

load_dotenv(override=True)

vector_store = Indexer(
    knowledge_base=KNOWLEDGE_BASE, db_name=DB_NAME, embeddings=EMBEDDINGS
).get_vector_store()
question = "Who is Avery?"
retriever = Retriever(vector_store)
rag = Rag(model_name=MODEL_NAME, retriever=retriever)
print(rag.answer_question(question)[0])
