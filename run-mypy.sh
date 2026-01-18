#!/bin/bash
set -euo pipefail

source .venv/bin/activate

mypy --cache-dir .mypy_cache --sqlite-cache --explicit-package-bases src/
