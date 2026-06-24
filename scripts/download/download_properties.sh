#!/bin/bash
source .venv/bin/activate
poetry run python scripts/download_wikidata_entity.py "$@"
