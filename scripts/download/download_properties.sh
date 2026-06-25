#!/bin/bash
cd "$(dirname "$0")/../.."
poetry run python scripts/download_wikidata_entity.py "$@"
