import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.chat import ChatHistory
from app.schemas.rag_schemas import (
    RAGChatRequest,
    RAGChatResponse,
    RAGIngestRequest,
    RAGQueryRequest,
    RAGQueryResponse,
)
from app.services.rag import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()
rag_service = RAGService()


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_document_text(request: RAGIngestRequest):
    """
    Ingests raw extracted document text.
    Chunks content, runs embeddings, and registers segments in vector storage.
    """
    try:
        chunk_count = rag_service.ingest_document(
            company_id=request.company_id,
            document_id=request.document_id,
            document_type=request.document_type,
            text=request.text_content
        )
        return {
            "status": "success",
            "message": f"Successfully ingested document '{request.document_id}'.",
            "chunks_count": chunk_count
        }
    except Exception as e:
        logger.error(f"RAG ingestion failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest document contents."
        )


@router.post("/query", response_model=RAGQueryResponse)
async def query_semantic_context(request: RAGQueryRequest):
    """
    Retrieves and reranks matching semantic segments scoping search to target tenant.
    """
    try:
        results = rag_service.retrieve_and_rerank(
            company_id=request.company_id,
            query=request.query,
            top_k=request.top_k
        )
        return RAGQueryResponse(query=request.query, results=results)
    except Exception as e:
        logger.error(f"RAG query execution failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute query search."
        )


@router.post("/chat", response_model=RAGChatResponse)
async def chat_conversational_rag(
    request: RAGChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Conversational RAG execution endpoint.
    Performs retrieval, compiles LLM grounded output, and audits exchange in chat history logs.
    """
    tenant_uuid = uuid.UUID(request.company_id)
    user_uuid = uuid.UUID(request.user_id)
    session_uuid = uuid.UUID(request.session_id)

    # 1. Audit log User Prompt to database
    user_chat_record = ChatHistory(
        company_id=tenant_uuid,
        user_id=user_uuid,
        session_id=session_uuid,
        role="user",
        message=request.message,
        metadata_info=None
    )
    db.add(user_chat_record)
    await db.flush()

    # 2. Run grounded response retrieval & generation
    try:
        answer, sources = rag_service.generate_chat_response(
            company_id=request.company_id,
            query=request.message
        )
    except Exception as e:
        logger.error(f"Failed to generate RAG response: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete assistant response generation."
        )

    # 3. Audit log Assistant Response to database
    assistant_chat_record = ChatHistory(
        company_id=tenant_uuid,
        user_id=user_uuid,
        session_id=session_uuid,
        role="assistant",
        message=answer,
        metadata_info={"sources_count": len(sources)}
    )
    db.add(assistant_chat_record)
    
    # Commit conversation history transaction
    await db.commit()

    return RAGChatResponse(
        session_id=request.session_id,
        answer=answer,
        sources=sources
    )
