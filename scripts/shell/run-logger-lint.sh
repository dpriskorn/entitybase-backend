#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

python scripts/linters/check_logger_debug.py src/