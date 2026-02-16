#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

source .venv/bin/activate

ruff check --fix --exit-non-zero-on-fix src/ tests/ # scripts/
ruff format src/ tests/ # scripts/
