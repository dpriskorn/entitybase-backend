.PHONY: lint test test-fast coverage help ruff mypy radon vulture

help:
	@echo "Available targets:"
	@echo "  make lint         - Run all linters"
	@echo "  make ruff         - Run ruff linter"
	@echo "  make mypy         - Run mypy type checker"
	@echo "  make radon        - Run radon complexity checker"
	@echo "  make vulture      - Run vulture dead code checker"
	@echo "  make test-fast   - Run unit tests only (fast feedback)"
	@echo "  make test        - Run all tests (unit + integration + e2e)"
	@echo "  make test-e2e    - Run e2e tests"
	@echo "  make test-integration-01 - Run integration tests (first 50)"
	@echo "  make test-integration-02 - Run integration tests (mid 50)"
	@echo "  make test-integration-03 - Run integration tests (late 50a)"
	@echo "  make test-integration-04 - Run integration tests (late 50b)"
	@echo "  make test-integration - Run all integration tests"
	@echo "  make coverage    - Run tests with coverage report"

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

test-fast:
	./run-unit-tests.sh

test:
	./run-all-tests.sh

test-e2e:
	./run-e2e-tests.sh

test-integration-01:
	./run-integration-01-first50.sh

test-integration-02:
	./run-integration-02-mid50.sh

test-integration-03:
	./run-integration-03-late50a.sh

test-integration-04:
	./run-integration-04-late50b.sh

test-integration: test-integration-01 test-integration-02 test-integration-03 test-integration-04

coverage:
	./run-coverage.sh
