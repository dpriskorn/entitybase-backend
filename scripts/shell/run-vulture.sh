#!/bin/bash
cd "$(dirname "$0")/../.."
vulture --config pyproject.toml src config/linters/allowlists/vulture.txt
