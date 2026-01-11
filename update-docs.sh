./run-scc.sh
./count-words.sh
./run-coverage.sh
python scripts/update-coverage-stats.py
python scripts/doc/extract_endpoints.py > src/models/rest_api/ENDPOINTS.md