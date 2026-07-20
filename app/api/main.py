from fastapi import FastAPI, HTTPException
from healthapi import router as health_router
from itemsapi import router as items_router
app = FastAPI()
app.include_router(health_router)
app.include_router(items_router, prefix="/api")
