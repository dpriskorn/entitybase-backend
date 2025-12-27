FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONPATH=/app/src

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    POETRY_NO_CACHE=1 poetry install --no-root

COPY ./src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "services.entity_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
