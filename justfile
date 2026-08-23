# Entitybase Backend task runner
# Requires: just (https://github.com/casey/just)

set shell := ["bash", "-cu"]

# List available recipes
@default:
    @just --list --list-heading "Available recipes:" --list-subheading ""

# Linting

lint:
    ./scripts/shell/run-linters.sh

ruff:
    ./scripts/shell/run-ruff.sh

mypy:
    ./scripts/shell/run-mypy.sh

radon:
    ./scripts/shell/run-radon.sh

vulture:
    ./scripts/shell/run-vulture.sh

# Unit tests (no Docker needed)

test-unit: test-unit-01 test-unit-02 test-unit-03 test-unit-04

test-unit-01:
    ./scripts/shell/run-unit-01-config-data.sh

test-unit-02:
    ./scripts/shell/run-unit-02-internal-workers.sh

test-unit-03:
    ./scripts/shell/run-unit-03-infra-rdf.sh

test-unit-04:
    ./scripts/shell/run-unit-04-rest-api.sh

# E2E tests (requires Docker: mysql, rustfs)

test-e2e: test-e2e-01 test-e2e-02 test-e2e-03 test-e2e-04

test-e2e-01:
    ./scripts/shell/run-e2e-01-basics.sh

test-e2e-02:
    ./scripts/shell/run-e2e-02-terms.sh

test-e2e-03:
    ./scripts/shell/run-e2e-03-user.sh

test-e2e-04:
    ./scripts/shell/run-e2e-04-advanced.sh

# Integration tests (requires running API)

test-integration: test-integration-01 test-integration-02 test-integration-03 test-integration-04

test-integration-01:
    ./scripts/shell/run-integration-01-first50.sh

test-integration-02:
    ./scripts/shell/run-integration-02-mid50.sh

test-integration-03:
    ./scripts/shell/run-integration-03-late50a.sh

test-integration-04:
    ./scripts/shell/run-integration-04-late50b.sh

# Contract tests (requires Docker)

test-contract:
    ./scripts/shell/run-contract.sh

# Combined test targets

test-fast: test-unit test-e2e test-contract

tests: test-unit test-e2e test-contract test-integration

lint-test-all: lint tests

lint-test-fast: lint test-fast

# Coverage

coverage:
    ./scripts/shell/run-coverage.sh

# Documentation

docs-generate:
    ./scripts/shell/update-docs.sh

docs-build:
    zensical build

docs-serve:
    zensical serve

docs: docs-generate docs-build docs-serve
