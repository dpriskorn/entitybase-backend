#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

poetry run ruff check --fix --exit-non-zero-on-fix src/ tests/ # scripts/
poetry run ruff format src/ tests/ # scripts/
