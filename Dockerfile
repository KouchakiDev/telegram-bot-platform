# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --system app && useradd --system --gid app --create-home app
WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY frontend ./frontend
COPY migrations ./migrations
COPY scripts ./scripts
COPY alembic.ini ./

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && python -m pip install . \
    && mkdir -p /app/data /app/logs \
    && chown -R app:app /app

USER app
EXPOSE 8000

CMD ["platform-web"]
