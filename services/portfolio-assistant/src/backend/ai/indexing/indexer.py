import glob
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader


class Indexer:
    """Builds (or reuses) a Chroma vector store from the knowledge base.

    1. Load documents from the knowledge base (``*.md``)
    2. Split them into chunks with the injected splitter
    3. Embed and persist them into Chroma

    A previously persisted store is reused as-is, so the index is built once and
    reloaded on subsequent runs instead of being rebuilt every time.
    """

    def __init__(self, knowledge_base, db_name, embeddings, splitter, max_documents=None) -> None:
        self._knowledge_base = knowledge_base  # folder of ".md" files
        self._db_name = db_name  # Chroma persistence directory
        self._embeddings = embeddings  # embeddings model
        self._splitter = splitter  # chunking strategy
        self._max_documents = max_documents  # optional cap (useful for tests)

    def _fetch_documents(self):
        """Loads every ``*.md`` document, tagging it with its folder doc_type."""
        documents = []
        for folder in glob.glob(str(Path(self._knowledge_base) / "*")):
            doc_type = os.path.basename(folder)  # company, contracts, employees, products
            loader = DirectoryLoader(
                folder,
                glob="**/*.md",
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"},
            )
            for doc in loader.load():
                doc.metadata["doc_type"] = doc_type
                documents.append(doc)
        return documents

    def _existing_store(self):
        """Returns the persisted Chroma store if one already holds vectors."""
        if os.path.isdir(self._db_name) and os.listdir(self._db_name):
            store = Chroma(persist_directory=self._db_name, embedding_function=self._embeddings)
            if store._collection.count() > 0:
                return store
        return None

    def get_vector_store(self):
        """Returns the vector store, reusing a persisted one when available."""
        existing = self._existing_store()
        if existing is not None:
            return existing

        documents = self._fetch_documents()
        if self._max_documents:
            documents = documents[: self._max_documents]
        chunks = self._splitter.split_documents(documents)
        return Chroma.from_documents(
            documents=chunks,
            embedding=self._embeddings,
            persist_directory=self._db_name,
        )
