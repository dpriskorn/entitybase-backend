#!/bin/bash
source .venv/bin/activate
vulture --config pyproject.toml src config/linters/allowlists/vulture.txt
