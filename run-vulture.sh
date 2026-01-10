#!/bin/bash
source .venv/bin/activate
vulture src vulture_allowlist.txt
