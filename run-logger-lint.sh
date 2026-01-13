#!/bin/bash
set -Eeuo pipefail

source .venv/bin/activate

python scripts/linters/check_logger_info.py src/