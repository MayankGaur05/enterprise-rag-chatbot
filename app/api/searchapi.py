from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.core.logging_config import setup_logging
from app.embeddings.openai_provider import OpenAIEmbeddingProvider
from app.retrieval.retriever import Retriever
from app.vectorstore.chroma_db import ChromaVectorStore

router = APIRouter()

settings = get_settings()
logger = setup_logging(settings.log_level)

class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query string.")
    top_k: int = Field(5, description="The number of top results to return.")   

class SearchResponse(BaseModel):
    query: str = Field(..., description="The search query string.")
    results: list[dict[str, Any]] = Field(..., description="List of search results.")   

@lru_cache
def get_retriever() -> Retriever:
    embedding_provider = OpenAIEmbeddingProvider()
    vector_store = ChromaVectorStore()
    return Retriever(embedding_provider=embedding_provider, vector_store=vector_store)

@router.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_documents(payload: SearchRequest):
    """
    Search for documents based on the provided query and return the top K results.
    """
    query = payload.query.strip()
    if not query:
        logger.error("Received empty query string in search request")
        raise HTTPException(status_code=400, detail="query must be a non-empty string")

    if payload.top_k < 1:
        raise HTTPException(status_code=400, detail="top_k must be at least 1")

    if payload.top_k > settings.retrieval_max_top_k:
        raise HTTPException(
            status_code=400,
            detail=f"top_k must be <= {settings.retrieval_max_top_k}",
        )

    try:
        retriever = get_retriever()
        results = retriever.search(query=query, top_k=payload.top_k)
        return SearchResponse(query=query, results=[asdict(r) for r in results])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Search failed | query={query} | error={exc}")
        raise HTTPException(status_code=500, detail="Search failed") from exc