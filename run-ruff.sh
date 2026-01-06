#!/bin/bash
source .venv/bin/activate
ruff check --fix src/ tests/ scripts/
ruff format src/ tests/ scripts/