#!/bin/bash
set -e
source .venv/bin/activate
PYTHONPATH=src poetry run pytest tests/contract/ -v -m contract
