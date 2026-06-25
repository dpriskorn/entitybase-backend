#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

poetry run pytest tests/contract/ -v -m contract
