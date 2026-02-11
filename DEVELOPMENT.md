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

## Development Workflow

- Make changes to the code
- Run tests: `./run-linters.sh` for linting
- Commit changes

## Troubleshooting

If you encounter issues with persistent data, ensure volumes are properly pruned as described in the setup steps.