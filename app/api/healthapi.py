from datetime import datetime, timezone

from fastapi import APIRouter

from app.config import get_settings
from app.core.logging_config import setup_logging

router = APIRouter()
logger = setup_logging(get_settings().log_level)

@router.get("/health", summary="Health Check", tags=["Health"])
def health_check(): 
    """
    Health check endpoint to verify the API is running.
    Returns the current server time in UTC.
    """
    response =  {
            "status": "ok", 
            "service": "enterprise-rag-chatbot",
            "message": "API is running",
            "timestamp": datetime.now(timezone.utc).isoformat()
            }
    logger.info(f"Health check requested: {response}")
    return response