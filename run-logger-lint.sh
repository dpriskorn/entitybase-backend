#!/bin/bash
set -Eeuo pipefail

source .venv/bin/activate

python scripts/check_logger_info.py src/