#!/bin/bash
# List the top 5 longest *.py files by line count, excluding .venv

find . -name "*.py" ! -path "./.venv/*" -print0 | xargs -0 wc -l | sort -nr | grep -v " total$" | head -5