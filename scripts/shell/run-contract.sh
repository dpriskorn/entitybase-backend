#!/bin/bash
set -e
source .venv/bin/activate
cd /home/dpriskorn/src/python/wikibase-backend
PYTHONPATH=src pytest tests/contract/ -v -m contract
