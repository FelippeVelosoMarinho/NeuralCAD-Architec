FROM python:3.10-slim-bookworm

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY alembic.ini ./
COPY alembic ./alembic
COPY src ./src
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# uvicorn neuralcad_api.main:app --host 0.0.0.0 --port 8000 (executado por entrypoint.sh após alembic upgrade head)

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app/src

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
