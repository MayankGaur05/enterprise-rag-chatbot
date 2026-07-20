from datetime import datetime, timezone

from fastapi import APIRouter

from pydantic import BaseModel, Field

router = APIRouter()

@router.get("/health", summary="Health Check", tags=["Health"])
def health_check(): 
    """
    Health check endpoint to verify the API is running.
    Returns the current server time in UTC.
    """
    return {
            "status": "ok", 
            "service": "enterprise-rag-chatbot",
            "message": "API is running",
            "timestamp": datetime.now(timezone.utc).isoformat()
            }