#!/bin/bash

source .venv/bin/activate
pytest -m "unit" -n auto
