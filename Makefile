.PHONY: lint test test-fast coverage help ruff mypy radon vulture stop api api-no-cache docs docs-generate docs-build docs-serve check

help:
	@echo "Available targets:"
	@echo "  make check         - Check if Docker services are running"
	@echo "  make api           - Run docker compose up and start the API locally using uvicorn with reload enabled"
	@echo "  make api-no-cache  - Run docker compose up with --no-cache (force rebuild all layers)"
	@echo "  make stop          - Stop docker and remove everything"
	@echo "  make lint         - Run all linters"
	@echo "  make ruff         - Run ruff linter"
	@echo "  make mypy         - Run mypy type checker"
	@echo "  make radon        - Run radon complexity checker"
	@echo "  make vulture      - Run vulture dead code checker"
	@echo "  make docs-generate - Generate documentation from code (statistics, endpoints, etc.)"
	@echo "  make docs-build   - Build static documentation site (uses zensical)"
	@echo "  make docs-serve   - Serve documentation locally with live reload (uses zensical)"
	@echo "  make docs         - Run docs-generate + docs-build + docs-serve"
	@echo "  make lint-test-all - Run all lint + tests (unit -> E2E -> contract -> integration)"
	@echo "  make lint-test-fast        - Run lint + fast tests (unit -> E2E)"
	@echo "  make tests        - Run all tests (unit -> E2E -> contract -> integration)"
	@echo "  make test-unit   - Run unit tests only (fast feedback)"
	@echo "  make test-e2e     - Run all e2e tests"
	@echo "  make test-e2e-01 - Run e2e tests (basics)"
	@echo "  make test-e2e-02 - Run e2e tests (terms)"
	@echo "  make test-e2e-03 - Run e2e tests (user features)"
	@echo "  make test-e2e-04 - Run e2e tests (advanced)"
	@echo "  make test-contract - Run contract tests (API schema validation)"
	@echo "  make test-integration-01 - Run integration tests (first 50)"
	@echo "  make test-integration-02 - Run integration tests (mid 50)"
	@echo "  make test-integration-03 - Run integration tests (late 50a)"
	@echo "  make test-integration-04 - Run integration tests (late 50b)"
	@echo "  make test-integration - Run all integration tests"
	@echo "  make test-unit-01 - Run unit tests (config, data, services, validation, json_parser)"
	@echo "  make test-unit-02 - Run unit tests (internal_representation, workers)"
	@echo "  make test-unit-03 - Run unit tests (infrastructure, rdf_builder)"
	@echo "  make test-unit-04 - Run unit tests (rest_api)"
	@echo "  make coverage    - Run tests with coverage report"

check:
	./scripts/shell/check-docker-services.sh

api:
	./scripts/shell/run-api-local.sh

api-no-cache:
	./scripts/shell/run-api-local.sh --no-cache

stop:
	./scripts/shell/stop-docker-and-remove-everything.sh

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

test-contract: check
	./scripts/shell/run-contract.sh

docs-generate:
	./scripts/shell/update-docs.sh

docs-build:
	zensical build

docs-serve:
	zensical serve

docs: docs-generate docs-build docs-serve

test-unit: test-unit-01 test-unit-02 test-unit-03 test-unit-04

test-unit-01:
	./scripts/shell/run-unit-01-config-data.sh

test-unit-02:
	./scripts/shell/run-unit-02-internal-workers.sh

test-unit-03:
	./scripts/shell/run-unit-03-infra-rdf.sh

test-unit-04:
	./scripts/shell/run-unit-04-rest-api.sh

test-e2e-01:
	./scripts/shell/run-e2e-01-basics.sh

test-e2e-02:
	./scripts/shell/run-e2e-02-terms.sh

test-e2e-03:
	./scripts/shell/run-e2e-03-user.sh

test-e2e-04:
	./scripts/shell/run-e2e-04-advanced.sh

test-e2e: check test-e2e-01 test-e2e-02 test-e2e-03 test-e2e-04

test-unit-e2e: test-unit test-e2e

test-integration-01:
	./scripts/shell/run-integration-01-first50.sh

test-integration-02:
	./scripts/shell/run-integration-02-mid50.sh

test-integration-03:
	./scripts/shell/run-integration-03-late50a.sh

test-integration-04:
	./scripts/shell/run-integration-04-late50b.sh

test-integration: check test-integration-01 test-integration-02 test-integration-03 test-integration-04

tests: check test-unit test-e2e test-contract test-integration-01 test-integration-02 test-integration-03 test-integration-04

lint-test-all: lint tests

lint-test-fast: lint test-unit-e2e

coverage: check
	./scripts/shell/run-coverage.sh
