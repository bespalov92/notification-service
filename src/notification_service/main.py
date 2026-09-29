from fastapi import FastAPI

from notification_service.config import settings

app = FastAPI(
    title=settings.application.app_name,
    debug=settings.application.debug
)


@app.get("/health", tags=["health"], include_in_schema=False)
async def check_health() -> dict[str, str]:
    return {"status": "ok"}
