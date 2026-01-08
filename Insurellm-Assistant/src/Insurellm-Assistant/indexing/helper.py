from langchain_core.documents.base import Document
from indexing.constants import AVERAGE_CHUNK_SIZE


def make_prompt(document: Document, chunk_size: int = AVERAGE_CHUNK_SIZE):
    how_many = (len(document.page_content) // chunk_size) + 1
    return f"""
    You take a document and you split the document into overlapping chunks for a KnowledgeBase.

    The document is from the shared drive of a company called Insurellm.
    The document is of type: {document.metadata["doc_type"]}
    The document has been retrieved from: {document.metadata["source"]}

    A chatbot will use these chunks to answer questions about the company.
    You should divide up the document as you see fit, being sure that the entire document is returned in the chunks - don't leave anything out.
    This document should probably be split into {how_many} chunks, but you can have more or less as appropriate.
    There should be overlap between the chunks as appropriate; typically about 25% overlap or about 50 words, so you have the same text in multiple chunks for best retrieval results.

    For each chunk, you should provide a headline, a summary, and the original text of the chunk.
    Together your chunks should represent the entire document with overlap.

    Here is the document:

    {document.page_content}

    Respond with the chunks.
    """


def make_messages(document: Document):
    return [
        {"role": "user", "content": make_prompt(document)},
    ]
