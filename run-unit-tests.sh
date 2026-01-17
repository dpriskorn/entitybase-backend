#!/bin/bash

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

pytest -m "unit" -n auto
