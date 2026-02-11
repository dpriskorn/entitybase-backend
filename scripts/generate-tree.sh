#!/bin/bash

# Generate directory tree for src/ excluding __pycache__
echo "# Tree" > src/TREE.md
echo '```' >> src/TREE.md
tree -d -I '__pycache__' src/ >> src/TREE.md
echo '```' >> src/TREE.md

echo "TREE.md generated in src/"