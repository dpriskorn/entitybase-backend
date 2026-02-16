#!/bin/bash
cd "$(dirname "$0")/../.."
"""Run the mock linter for integration tests."""

python3 scripts/linters/mock_linter.py