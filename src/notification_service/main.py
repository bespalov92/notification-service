from fastapi import FastAPI

app = FastAPI(
    title="Notification service",
)


@app.get("/health", tags=["health"], include_in_schema=False)
async def check_health() -> dict[str, str]:
    return {"status": "ok"}
