#!/bin/bash
set -e

export PYTHONPATH=/home/dpriskorn/src/python/wikibase-backend/src:$PYTHONPATH

./run-ruff.sh
./run-mypy.sh
./run-vulture.sh