from fastapi import FastAPI

from notification_service.config import ApplicationSettings

app_settings = ApplicationSettings()

app = FastAPI(
    title=app_settings.app_name,
    debug=app_settings.debug
)


@app.get("/health", tags=["health"], include_in_schema=False)
async def check_health() -> dict[str, str]:
    return {"status": "ok"}
