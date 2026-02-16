# Development Environment Setup

This document describes how to set up and run the Enitybase Backend development environment using Docker.

## Prerequisites

- Docker and Docker Compose installed
- Git

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd entitybase-backend
   ```

2. Ensure Docker is running.

## Running the Development Environment

To start the development environment with a pristine state:

   ```bash
   ./run-docker-build-tests.sh`
   ```
This process ensures a clean database and environment each time, as all volumes are deleted and recreated.

## Running Tests

### Unit Tests Locally

To run unit tests locally without Docker:

   ```bash
   ./run-unit-tests.sh
   ```

If pytest is not found, install it via `pip install pytest` or activate your virtual environment.

### Integration Tests

Integration tests need docker to be able to access minio and mysql.
The database is reset between tests, providing a clean state for each test run.

   ```bash
   ./run-integration-tests.sh
   ```

### End-to-end (E2E) Tests

E2E tests need docker to be able to access minio and mysql.
The database is reset between tests, providing a clean state for each test run.

   ```bash
   ./run-e2e-tests.sh
   ```

## Makefile Commands

This project uses a Makefile for common development tasks. Run `make help` to see all available targets.

### Running the API

| Command | Description |
|---------|-------------|
| `make api` | Start the API locally using uvicorn with reload enabled (requires Docker for MySQL and MinIO) |

### Linting and Code Quality

| Command | Description |
|---------|-------------|
| `make lint` | Run all linters (ruff, mypy, radon, vulture) |
| `make ruff` | Run ruff linter |
| `make mypy` | Run mypy type checker |
| `make radon` | Run radon complexity checker |
| `make vulture` | Run vulture dead code checker |

### Testing

#### Unit Tests

| Command | Description |
|---------|-------------|
| `make test-unit` | Run all unit tests |
| `make test-unit-01` | Unit tests: config, data, services, validation, json_parser |
| `make test-unit-02` | Unit tests: internal_representation, workers |
| `make test-unit-03` | Unit tests: infrastructure, rdf_builder |
| `make test-unit-04` | Unit tests: rest_api |

#### End-to-End Tests

| Command | Description |
|---------|-------------|
| `make test-e2e` | Run all e2e tests |
| `make test-e2e-01` | E2E tests: basics |
| `make test-e2e-02` | E2E tests: terms |
| `make test-e2e-03` | E2E tests: user features |
| `make test-e2e-04` | E2E tests: advanced |

#### Contract Tests

| Command | Description |
|---------|-------------|
| `make test-contract` | Run contract tests (API schema validation) |

#### Integration Tests

| Command | Description |
|---------|-------------|
| `make test-integration` | Run all integration tests |
| `make test-integration-01` | Integration tests: first 50 |
| `make test-integration-02` | Integration tests: mid 50 |
| `make test-integration-03` | Integration tests: late 50a |
| `make test-integration-04` | Integration tests: late 50b |

#### Combined Commands

| Command | Description |
|---------|-------------|
| `make tests` | Run all tests (unit → e2e → contract → integration) |
| `make lint-test-fast` | Run lint + unit tests + e2e tests |
| `make lint-test-all` | Run lint + all tests (unit → e2e → contract → integration) |
| `make coverage` | Run tests with coverage report |

## Development Workflow

- Make changes to the code
- Run tests: `./run-linters.sh` for linting
- Commit changes

## Troubleshooting

If you encounter issues with persistent data, ensure volumes are properly pruned as described in the setup steps.