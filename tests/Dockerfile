FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install pytest requests fastapi httpx pytest-asyncio rapidhash rdflib pydantic-settings pymysql boto3 jsonschema aiokafka


COPY ./tests/ ./tests/
COPY ./src/ ./src/
COPY ./test_data/ ./test_data/
COPY pytest.ini .

ENV PYTHONPATH=/app/src

CMD sleep 10 && pytest tests/ -v --tb=short --log-cli-level=DEBUG --exitfirst
#CMD ["pytest", "tests/", "-v", "--tb=short", "--log-cli-level=DEBUG"]
