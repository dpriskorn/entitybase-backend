# Setup Guide

Complete environment setup for Entitybase Backend.

## Requirements

- Python 3.13+
- Docker & Docker Compose
- Poetry
- AWS credentials (for S3)

## Environment Variables

Create a `.env` file:

```bash
# Database
DATABASE_HOST=localhost
DATABASE_PORT=33306
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_NAME=wikibase

# S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=your-bucket
S3_REGION=us-east-1

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## Docker Setup

```bash
# Start all services (Vitess, API, workers)
make api

# Stop everything
make stop
```

## Local Development

```bash
# Install dependencies
poetry install --with dev

# Activate virtual environment
source .venv/bin/activate

# Run tests
make test-unit
make test-integration

# Run linters
make lint
```

## Running Services Individually

```bash
# Start Vitess only
docker compose up vitess

# Start API only
uvicorn src.models.rest_api.main:app --reload
```
