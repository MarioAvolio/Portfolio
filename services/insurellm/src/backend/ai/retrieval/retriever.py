class Retriever:
    """
    Retrieve relevant context documents for a question.
    """
    def __init__(self, vector_store, k=10) -> None:
        self._vector_store = vector_store
        self.k = k
        self._retriever = self._vector_store.as_retriever()
    
    def fetch_context(self, question):
        return self._retriever.invoke(question, k=self.k)    
