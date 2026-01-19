#!/bin/bash

source .venv/bin/activate
export PYTHONPATH=src
pytest tests/unit/ -n auto
