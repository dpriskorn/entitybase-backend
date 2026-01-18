#!/bin/bash

source .venv/bin/activate
export PYTHONPATH=src
pytest -m "unit" -n auto
