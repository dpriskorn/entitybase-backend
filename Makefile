.PHONY: be-lint be-test-fast be-coverage help stop docs docs-generate docs-build docs-serve check release push-release ci fe-lint fe-tests fe-run be-tests be-test-unit be-test-e2e be-test-contract be-test-integration

help:
	@echo "Available targets:"
	@echo "  make check         - Check if Docker services are running"
	@echo "  make api           - Run docker compose up and start the API locally using uvicorn with reload enabled"
	@echo "  make api-no-cache  - Run docker compose up with --no-cache (force rebuild all layers)"

	@echo "  make ci            - Run CI simulation locally (mimics GitHub CI workflow)"
	@echo "  make stop          - Stop docker and remove everything"
	@echo "  make release       - Create tag locally (e.g., v2026.2.28)"
	@echo "  make push-release - Create tag and push to trigger GitHub release workflow"
	@echo "  make be-lint         - Run all linters"
	@echo "  make docs-generate - Generate documentation from code (statistics, endpoints, etc.)"
	@echo "  make docs-build   - Build static documentation site (uses zensical)"
	@echo "  make docs-serve   - Serve documentation locally with live reload (uses zensical)"
	@echo "  make docs         - Run docs-generate + docs-build + docs-serve"
	@echo "  make be-lint-test-all - Run all lint + tests (unit -> E2E -> contract -> integration)"
	@echo "  make be-lint-test-fast        - Run lint + fast tests (unit -> E2E -> contract)"
	@echo "  make be-test-fast        - Run fast tests (unit -> E2E -> contract)"
	@echo "  make be-tests        - Run all tests (unit -> E2E -> contract -> integration)"
	@echo "  make be-test-unit   - Run unit tests only (fast feedback)"
	@echo "  make be-test-e2e     - Run all e2e tests"
	@echo "  make be-test-e2e-01 - Run e2e tests (basics)"
	@echo "  make be-test-e2e-02 - Run e2e tests (terms)"
	@echo "  make be-test-e2e-03 - Run e2e tests (user features)"
	@echo "  make be-test-e2e-04 - Run e2e tests (advanced)"
	@echo "  make be-test-contract - Run contract tests (API schema validation)"
	@echo "  make be-test-integration-01 - Run integration tests (first 50)"
	@echo "  make be-test-integration-02 - Run integration tests (mid 50)"
	@echo "  make be-test-integration-03 - Run integration tests (late 50a)"
	@echo "  make be-test-integration-04 - Run integration tests (late 50b)"
	@echo "  make be-test-integration - Run all integration tests"
	@echo "  make be-test-unit-01 - Run unit tests (config, data, services, validation, json_parser)"
	@echo "  make be-test-unit-02 - Run unit tests (internal_representation, workers)"
	@echo "  make be-test-unit-03 - Run unit tests (infrastructure, rdf_builder)"
	@echo "  make be-test-unit-04 - Run unit tests (rest_api)"
	@echo "  make be-coverage    - Run tests with coverage report"
	@echo "  make fe-lint     - Run frontend linter (eslint/prettier)"
	@echo "  make fe-test     - Run frontend tests (vitest)"
	@echo "  make fe-run      - Run frontend dev server"

check:
	./scripts/shell/check-docker-services.sh

ci:
	./scripts/shell/run-ci-local.sh

stop:
	./scripts/shell/stop-docker-and-remove-everything.sh

release:
	./scripts/shell/run-release.sh

push-release:
	make release && git push origin $$(cat .release_version | cut -d= -f2) && rm -f .release_version

be-lint:
	./scripts/shell/run-linters.sh

be-test-contract: check
	./scripts/shell/run-contract.sh

docs-generate:
	./scripts/shell/update-docs.sh

docs-build:
	zensical build

docs-serve:
	zensical serve

docs: docs-generate docs-build docs-serve

be-test-unit: be-test-unit-01 be-test-unit-02 be-test-unit-03 be-test-unit-04

be-test-unit-01:
	./scripts/shell/run-unit-01-config-data.sh

be-test-unit-02:
	./scripts/shell/run-unit-02-internal-workers.sh

be-test-unit-03:
	./scripts/shell/run-unit-03-infra-rdf.sh

be-test-unit-04:
	./scripts/shell/run-unit-04-rest-api.sh

be-test-e2e-01:
	./scripts/shell/run-e2e-01-basics.sh

be-test-e2e-02:
	./scripts/shell/run-e2e-02-terms.sh

be-test-e2e-03:
	./scripts/shell/run-e2e-03-user.sh

be-test-e2e-04:
	./scripts/shell/run-e2e-04-advanced.sh

be-test-e2e: check be-test-e2e-01 be-test-e2e-02 be-test-e2e-03 be-test-e2e-04

be-test-unit-e2e-contract: be-test-unit be-test-e2e be-test-contract

be-test-integration-01:
	./scripts/shell/run-integration-01-first50.sh

be-test-integration-02:
	./scripts/shell/run-integration-02-mid50.sh

be-test-integration-03:
	./scripts/shell/run-integration-03-late50a.sh

be-test-integration-04:
	./scripts/shell/run-integration-04-late50b.sh

be-test-integration: check be-test-integration-01 be-test-integration-02 be-test-integration-03 be-test-integration-04

be-tests: check be-test-unit be-test-e2e be-test-contract be-test-integration

lint-test-all: be-lint be-tests

lint-test-fast: be-lint be-test-unit-e2e-contract

be-test-fast: be-test-unit-e2e-contract

be-coverage: check
	./scripts/shell/run-coverage.sh

fe-lint:
	cd frontend && npm run lint

fe-tests:
	cd frontend && npm run test

fe-run:
	cd frontend && npm run dev
