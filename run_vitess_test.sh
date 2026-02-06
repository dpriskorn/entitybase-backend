#!/bin/bash
source .venv/bin/activate
export PYTHONPATH=src
pytest tests/unit/models/infrastructure/vitess/test_vitess_client.py -v
