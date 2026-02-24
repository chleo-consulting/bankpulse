from fastapi import FastAPI

from api.router import api_router
from core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router)


@app.get("/health", tags=["Infrastructure"])
async def health_check() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION, "service": settings.APP_NAME}
