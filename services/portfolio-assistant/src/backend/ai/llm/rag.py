from langchain_core.messages import HumanMessage, SystemMessage, convert_to_messages
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document


class Rag:
    def __init__(self, model_name, retriever) -> None:
        self._llm = ChatOpenAI(
            temperature=0, model_name=model_name  # more deterministic
        )

        self._system_prompt = """
                                You are a knowledgeable, friendly assistant representing the company Insurellm.
                                You are chatting with a user about Insurellm.
                                If relevant, use the given context to answer any question.
                                If you don't know the answer, say so.
                                Context:
                                {context}
                                """

        self._retriever = retriever

    def _combined_question(self, question: str, history: list[dict] = []) -> str:
        """
        Combine all the user's messages into a single string.
        """
        prior = "\n".join(m["content"] for m in history if m["role"] == "user")
        return prior + "\n" + question

    def answer_question(self, question: str, history: list[dict] = []):
        combined = self._combined_question(question, history)
        docs = self._retriever.fetch_context(
            combined
        )  # retrive all the document near our context (question + previous questions)
        context = "\n\n".join(doc.page_content for doc in docs)

        # update system_prompt
        system_prompt = self._system_prompt.format(context=context)

        # insert system prompt
        messages = [SystemMessage(content=system_prompt)]

        # insert previous hystory
        messages.extend(convert_to_messages(history))

        # insert last question
        messages.append(HumanMessage(content=question))

        response = self._llm.invoke(messages)

        return response.content, docs
