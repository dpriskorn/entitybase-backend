#!/bin/bash
set -e
export PYTHONPATH=src
poetry run pytest tests/contract/ -v -m contract
