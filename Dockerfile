FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /uvx /bin/

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-dev

COPY src ./src

RUN groupadd --system app \
    && useradd --system --gid app app

USER app

EXPOSE 8000

CMD ["uvicorn", "notification_service.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]