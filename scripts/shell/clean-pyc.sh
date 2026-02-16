#!/bin/bash
cd "$(dirname "$0")/../.."
# Clean Python cache files
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete