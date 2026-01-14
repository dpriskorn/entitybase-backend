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

1. Stop any running containers and remove volumes:
   ```bash
   docker compose down
   docker volume prune -f
   ```

2. Start the services:
   ```bash
   docker compose up
   ```

This process ensures a clean database and environment each time, as all volumes are deleted and recreated.

## Running Tests

Integration tests can be run within the Docker environment. The database is reset between builds, providing a clean state for each test run.

## Development Workflow

- Make changes to the code
- Run tests: `./run-linters.sh` for linting, integration tests via Docker
- Commit changes

## Troubleshooting

If you encounter issues with persistent data, ensure volumes are properly pruned as described in the setup steps.