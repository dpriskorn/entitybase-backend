#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

./scripts/linters/value_error_linter.py