# Development Environment Setup

This document describes how to set up and run the Wikibase Backend development environment using Docker.

## Prerequisites

- Docker and Docker Compose installed
- Git

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd wikibase-backend
   ```

2. Ensure Docker is running.

## Running the Development Environment

To start the development environment with a pristine state:

   ```bash
   ./run-docker-build.sh`
   ```
This process ensures a clean database and environment each time, as all volumes are deleted and recreated.

## Running Tests

### Integration Tests

Integration tests can be run within the Docker environment. The database is reset between builds, providing a clean state for each test run.

### Unit Tests Locally

To run unit tests locally without Docker:

   ```bash
   ./run-unit-tests.sh
   ```

If pytest is not found, install it via `pip install pytest` or activate your virtual environment.

## Development Workflow

- Make changes to the code
- Run tests: `./run-linters.sh` for linting, integration tests via Docker
- Commit changes

## Troubleshooting

If you encounter issues with persistent data, ensure volumes are properly pruned as described in the setup steps.