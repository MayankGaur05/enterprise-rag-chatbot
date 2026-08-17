from fastapi import FastAPI

from app.api.healthapi import router as health_router
from app.api.ingestionapi import router as ingestion_router
from app.api.itemsapi import router as items_router
from app.api.searchapi import router as search_router
from app.config import get_settings
from app.core.logging_config import setup_logging

settings = get_settings()
logger = setup_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(items_router, prefix="/api")
app.include_router(ingestion_router, prefix="/api")
app.include_router(search_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting up {settings.app_name} in {settings.environment} environment")
    logger.info(f"API is running on {settings.api_host}:{settings.api_port}")
    logger.info(f"Streamlit is running on port {settings.streamlit_port}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.app_name}")       