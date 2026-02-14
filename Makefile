.PHONY: lint test test-fast coverage help ruff mypy radon vulture

help:
	@echo "Available targets:"
	@echo "  make api         - Run docker compose up and start the API locally using uvicorn with reload enabled"
	@echo "  make lint         - Run all linters"
	@echo "  make ruff         - Run ruff linter"
	@echo "  make mypy         - Run mypy type checker"
	@echo "  make radon        - Run radon complexity checker"
	@echo "  make vulture      - Run vulture dead code checker"
	@echo "  make lint-test-all - Run all lint + tests (unit -> E2E -> integration)"
	@echo "  make lint-test-fast        - Run lint + fast tests (unit -> E2E)"
	@echo "  make tests        - Run all tests (unit -> E2E -> integration)"
	@echo "  make test-unit   - Run unit tests only (fast feedback)"
	@echo "  make test-e2e     - Run all e2e tests"
	@echo "  make test-e2e-01 - Run e2e tests (basics)"
	@echo "  make test-e2e-02 - Run e2e tests (terms)"
	@echo "  make test-e2e-03 - Run e2e tests (user features)"
	@echo "  make test-e2e-04 - Run e2e tests (advanced)"
	@echo "  make test-integration-01 - Run integration tests (first 50)"
	@echo "  make test-integration-02 - Run integration tests (mid 50)"
	@echo "  make test-integration-03 - Run integration tests (late 50a)"
	@echo "  make test-integration-04 - Run integration tests (late 50b)"
	@echo "  make test-integration - Run all integration tests"
	@echo "  make coverage    - Run tests with coverage report"

api:
	./run-api-local.sh

lint:
	./run-linters.sh

ruff:
	./run-ruff.sh

mypy:
	./run-mypy.sh

radon:
	./run-radon.sh

vulture:
	./run-vulture.sh

test-unit:
	./run-unit-tests.sh

test-e2e:
	./run-e2e-tests.sh

test-e2e-01:
	./run-e2e-01-basics.sh

test-e2e-02:
	./run-e2e-02-terms.sh

test-e2e-03:
	./run-e2e-03-user.sh

test-e2e-04:
	./run-e2e-04-advanced.sh

test-unit-e2e: test-unit test-e2e

test-integration-01:
	./run-integration-01-first50.sh

test-integration-02:
	./run-integration-02-mid50.sh

test-integration-03:
	./run-integration-03-late50a.sh

test-integration-04:
	./run-integration-04-late50b.sh

test-integration: test-integration-01 test-integration-02 test-integration-03 test-integration-04

tests: test-unit test-e2e test-integration-01 test-integration-02 test-integration-03 test-integration-04

lint-test-all: lint tests

lint-test-fast: lint test-unit-e2e

coverage:
	./run-coverage.sh
