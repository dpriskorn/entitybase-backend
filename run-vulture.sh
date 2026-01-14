#!/bin/bash
source .venv/bin/activate
vulture src config/linters/allowlists/vulture.txt
