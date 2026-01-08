from langchain_core.documents.base import Document
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from indexing.constants import AVERAGE_CHUNK_SIZE
from indexing.helper import make_messages
from tqdm import tqdm


class Chunk(BaseModel):
    """A class to perfectly represent a chunk"""

    headline: str = Field(
        description="A brief heading for this chunk, typically a few words, that is most likely to be surfaced in a query"
    )
    summary: str = Field(
        description="A few sentences summarizing the content of this chunk to answer common questions"
    )
    original_text: str = Field(
        description="The original text of this chunk from the provided document, exactly as is, not changed in any way"
    )

    def as_document(self, document):
        metadata = {
            "source": document.metadata["source"],
            "doc_type": document.metadata["doc_type"],
        }
        return Document(
            page_content=self.headline
            + "\n\n"
            + self.summary
            + "\n\n"
            + self.original_text,
            metadata=metadata,
        )


class Chunks(BaseModel):
    chunks: list[Chunk]


class CustomTextSplitter:
    def __init__(
        self, model: str = "gpt-4.1-nano", chunk_size: int = AVERAGE_CHUNK_SIZE
    ):
        self._chunk_size = chunk_size
        self._openai = ChatOpenAI(temperature=0, model=model).with_structured_output(
            Chunks
        )

    def _split_document(self, document: Document):
        messages = make_messages(document)
        response = self._openai.invoke(messages)
        return [chunk.as_document(document) for chunk in response.chunks]

    def split_documents(self, documents: list[Document]) -> list[Document]:
        chunks = []
        for document in tqdm(documents):
            chunks.extend(self._split_document(document))
        print(f"Chunks created: {len(chunks)}")
        return chunks
