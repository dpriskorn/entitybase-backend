#!/bin/bash
cd "$(dirname "$0")/../.."
poetry run vulture --config pyproject.toml src config/linters/allowlists/vulture.txt
