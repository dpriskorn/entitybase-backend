#!/bin/bash
source .venv/bin/activate
python scripts/download_wikidata_entity.py "$@"
