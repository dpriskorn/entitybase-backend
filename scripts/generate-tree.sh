#!/bin/bash

# Generate directory tree for src/ excluding __pycache__
tree -d -I '__pycache__' src/ > src/TREE.md

echo "TREE.md generated in src/"