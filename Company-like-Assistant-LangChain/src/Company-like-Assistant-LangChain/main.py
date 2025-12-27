from indexing.indexer import Indexer
from constants import DB_NAME, EMBEDDINGS, KNOWLEDGE_BASE

vector_store = Indexer(knowledge_base=KNOWLEDGE_BASE, db_name = DB_NAME, embeddings=EMBEDDINGS).get_vector_store()
