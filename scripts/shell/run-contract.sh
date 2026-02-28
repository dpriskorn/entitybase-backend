#!/bin/bash
set -e
source .venv/bin/activate
PYTHONPATH=src pytest tests/contract/ -v -m contract
