#!/bin/bash
set -e

source .venv/bin/activate

mypy src/ tests/ scripts/
