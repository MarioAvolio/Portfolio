from langchain_core.messages import HumanMessage, SystemMessage, convert_to_messages
from langchain_openai import ChatOpenAI


class Rag:
    def __init__(self, model_name, retriever) -> None:
        self._llm = ChatOpenAI(
            temperature=0, model_name=model_name  # more deterministic
        )

        self._system_prompt = """
                                You are a knowledgeable assistant for Mario Avolio's professional portfolio.
                                You help recruiters, collaborators, and visitors learn about Mario's
                                background, skills, projects, experience, education, and publications.
                                Answer questions about Mario concisely and accurately.
                                If relevant, use the given context to answer any question.
                                If you don't know the answer, say so.
                                Context:
                                {context}
                                """

        self._retriever = retriever

    def _combined_question(self, question: str, history: list[dict] | None = None) -> str:
        """Combine all user messages into a single context string.

        Args:
            question: The current user question.
            history: Prior conversation turns as {"role": ..., "content": ...} dicts.

        Returns:
            Concatenated prior user messages + current question.
        """
        if history is None:
            history = []
        prior = "\n".join(m["content"] for m in history if m["role"] == "user")
        return prior + "\n" + question

    def answer_question(self, question: str, history: list[dict] | None = None):
        """Generate a grounded answer using the RAG pipeline.

        Args:
            question: The current user question.
            history: Prior conversation turns as {"role": ..., "content": ...} dicts.

        Returns:
            Tuple of (answer_text, source_documents).
        """
        if history is None:
            history = []
        combined = self._combined_question(question, history)
        docs = self._retriever.fetch_context(combined)
        context = "\n\n".join(doc.page_content for doc in docs)

        system_prompt = self._system_prompt.format(context=context)

        messages = [SystemMessage(content=system_prompt)]

        messages.extend(convert_to_messages(history))

        messages.append(HumanMessage(content=question))

        response = self._llm.invoke(messages)

        return response.content, docs
