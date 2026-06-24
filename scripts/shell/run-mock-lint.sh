#!/bin/bash
cd "$(dirname "$0")/../.."
"""Run the mock linter for integration tests."""

poetry run python scripts/linters/mock_linter.py