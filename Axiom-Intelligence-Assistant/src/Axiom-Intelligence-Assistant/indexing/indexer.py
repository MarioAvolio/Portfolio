import glob
import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

class Indexer:
    """
    1. Load documents from the knowledge base (*.md)
    2. Split into chunks
    3. Vector Embedding & Store them into Chroma 
    """
    def __init__(self, knowledge_base, db_name, embeddings) -> None:
        self._knowledge_base = knowledge_base
        self._db_name = db_name
        self._embeddings = embeddings
    
    def _fetch_documents(self):
        """
        Fetch all the company documents (*.md) from the assets folder
        """
        folders = glob.glob(str(Path(self._knowledge_base) / "*"))
        print(f"Folder: {folders}")

        documents = [] # list of LangChain Documents
        for folder in folders:
            doc_type = os.path.basename(folder) # company, contracts, employees, products
            loader = DirectoryLoader(folder, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding":"utf-8"})
            folder_docs = loader.load() # enter in a folder

            for doc in folder_docs:
                doc.metadata["doc_type"] = doc_type # insert doc type as metadata
                documents.append(doc)
        
        return documents
    
    def _create_chunks(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        return chunks

    
    def _create_embeddings(self, chunks):
        if os.path.exists(self._db_name):
            Chroma(persist_directory=self._db_name, embedding_function=self._embeddings).delete_collection() # remove previous databases
        
        vector_store = Chroma.from_documents(documents=chunks, embedding=self._embeddings, persist_directory=self._db_name) # create a new db

        # debug
        collection = vector_store._collection
        count = collection.count()
        sample_embedding = collection.get(limit=1, include=["embeddings"])["embeddings"][0]
        dimensions = len(sample_embedding)
        print(f"There are {count:,} vectors with {dimensions:,} dimensions in the vector store")
        #
        
        return vector_store

    def get_vector_store(self):
        documents = self._fetch_documents()
        print(f"Fetched documents: {len(documents)}")
        chunks = self._create_chunks(documents)
        print(f"Chunks created: {len(chunks)}")
        vector_store = self._create_embeddings(chunks)
        return vector_store

        


        




