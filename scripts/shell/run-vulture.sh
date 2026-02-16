#!/bin/bash
cd "$(dirname "$0")/../.."
source .venv/bin/activate
vulture src config/linters/allowlists/vulture.txt
