#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

./scripts/shell/run-scc.sh
git log --date=short --format='%ad' | sort | uniq -c | awk '{sum+=$1; count++} END {print "Average commits per day:", sum/count}' >> STATISTICS.md
./scripts/shell/count-tests.sh >> STATISTICS.md
./scripts/shell/count-words.sh
poetry run python scripts/doc/extract_endpoints.py
poetry run python scripts/doc/generate_workers_overview.py > docs/ARCHITECTURE/WORKERS.md
poetry run python scripts/doc/generate_services_overview.py > docs/ARCHITECTURE/SERVICES.md
poetry run python scripts/doc/generate_api_models_overview.py > docs/ARCHITECTURE/API_MODELS.md
poetry run python scripts/doc/generate_database_schema_overview.py > docs/ARCHITECTURE/DATABASE_SCHEMA.md
poetry run python scripts/doc/generate_configuration_overview.py > docs/ARCHITECTURE/CONFIGURATION.md
poetry run python scripts/doc/generate_repositories_overview.py > docs/ARCHITECTURE/REPOSITORIES.md
poetry run python scripts/doc/update_schemas_readme.py > schemas/README.md
poetry run python scripts/doc/generate_architecture_diagrams.py
poetry run python scripts/doc/generate_pngs.py
poetry run python scripts/generate_api_docs.py
./scripts/generate-tree.sh
