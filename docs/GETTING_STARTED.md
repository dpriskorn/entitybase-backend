# Quick Start

Get up and running with Entitybase Backend in 5 minutes.

## Prerequisites

- Python 3.13+
- Docker and Docker Compose
- Poetry (for local development)

## Option 1: Docker (Recommended)

```bash
# Start the full stack (Vitess, API, workers)
make api

# API runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Option 2: Local Development

```bash
# Install dependencies
poetry install --with dev

# Run tests to verify setup
make test-unit
```

## Verify It's Working

```bash
# Health check
curl http://localhost:8000/health

# Create your first item
curl -X POST http://localhost:8000/v1/entitybase/entities/items \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{"labels": {"en": {"value": "Hello World", "language": "en"}}}'
```

## Next Steps

- [Setup Guide](SETUP.md) - Full environment configuration
- [Project Structure](PROJECT_STRUCTURE.md) - Understanding the codebase
- [API Endpoints](ENDPOINTS.md) - Explore the REST API
