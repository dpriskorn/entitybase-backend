FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install

COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "services.entity-api.main:app", "--host", "0.0.0.0", "--port", "8000"]
