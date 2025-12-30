#!/bin/bash
source .venv/bin/activate
python src/scripts/download_properties_sparql.py "$@"
