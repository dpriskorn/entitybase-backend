#!/bin/bash
set -e

./run-ruff.sh
./run-mypy.sh
./run-vulture.sh