# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=UTC

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl tzdata unixodbc \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system app && useradd --system --gid app --create-home app
WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY scripts ./scripts
COPY migrations ./migrations
COPY frontend ./frontend
COPY docs ./docs
COPY alembic.ini ./
COPY resources ./resources

# Full feature-parity image. ODBC support remains runtime-only unless the selected DB needs it.
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && python -m pip install '.[legacy,legacy-db]' \
    && mkdir -p /app/data /app/logs \
    && chown -R app:app /app

USER app
EXPOSE 8000

CMD ["platform-web"]
