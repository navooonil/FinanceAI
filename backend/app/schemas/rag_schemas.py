from typing import List, Optional
from pydantic import BaseModel, Field


class RAGIngestRequest(BaseModel):
    """
    Schema for ingesting raw parsed text into the vector database.
    """
    company_id: str = Field(..., description="Tenancy identifier.")
    document_id: str = Field(..., description="UUID of source invoice or report.")
    document_type: str = Field(..., description="Document domain category (e.g. invoice, report).")
    text_content: str = Field(..., description="Raw text context to chunk and embed.")


class RAGQueryRequest(BaseModel):
    """
    Schema representing user similarity query payload.
    """
    company_id: str = Field(..., description="Tenancy boundary identifier.")
    query: str = Field(..., description="Semantic search query.")
    top_k: int = Field(default=5, description="Number of results to retrieve.")


class RerankedChunkSchema(BaseModel):
    """
    Schema representing a reranked similarity context passage.
    """
    text: str = Field(..., description="Snippet text segment content.")
    score: float = Field(..., description="Reranking relevance score.")
    document_id: str = Field(..., description="Source document UUID.")
    document_type: str = Field(..., description="Category of source document.")


class RAGQueryResponse(BaseModel):
    """
    Schema wrapping parsed similarity response contexts.
    """
    query: str
    results: List[RerankedChunkSchema]


class RAGChatRequest(BaseModel):
    """
    Schema for a conversational RAG session message.
    """
    company_id: str = Field(..., description="Tenant namespace identifier.")
    user_id: str = Field(..., description="User UUID initiating message.")
    session_id: str = Field(..., description="Grouping chat session UUID.")
    message: str = Field(..., description="User query message.")


class RAGChatResponse(BaseModel):
    """
    Response model for conversational RAG assistants.
    """
    session_id: str
    answer: str = Field(..., description="LLM generated answer grounded on matching sources.")
    sources: List[RerankedChunkSchema] = Field(default_factory=list, description="Retrieved contexts used to compile answer.")
