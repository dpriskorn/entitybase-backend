#!/bin/bash

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

pytest -m "not integration" -n auto
