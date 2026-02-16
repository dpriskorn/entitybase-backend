#!/bin/bash
cd "$(dirname "$0")/../.."
set -euo pipefail

source .venv/bin/activate

mypy \
  --cache-dir .mypy_cache \
  --sqlite-cache \
  --explicit-package-bases \
  --disable-error-code=union-attr \
  --disable-error-code=return-value \
  src/ # tests/
