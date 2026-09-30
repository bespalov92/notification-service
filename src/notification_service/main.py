from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from notification_service.config import get_settings
from notification_service.db.session import dispose_database

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    yield
    await dispose_database()


app = FastAPI(
    title=settings.application.app_name,
    debug=settings.application.debug,
    lifespan=lifespan
)


@app.get("/health", tags=["health"], include_in_schema=False)
async def check_health() -> dict[str, str]:
    return {"status": "ok"}
