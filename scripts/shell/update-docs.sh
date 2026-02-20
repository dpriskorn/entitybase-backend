#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

./scripts/shell/run-scc.sh
git log --date=short --format='%ad' | sort | uniq -c | awk '{sum+=$1; count++} END {print "Average commits per day:", sum/count}' >> STATISTICS.md
# python scripts/doc/generate_git_stats.py >> STATISTICS.md
./scripts/shell/count-tests.sh >> STATISTICS.md
./scripts/shell/count-words.sh
# ./scripts/shell/run-coverage.sh
# python scripts/doc/update-coverage-stats.py
python scripts/doc/extract_endpoints.py
python scripts/doc/generate_workers_overview.py > docs/ARCHITECTURE/WORKERS.md
python scripts/doc/generate_services_overview.py > docs/ARCHITECTURE/SERVICES.md
python scripts/doc/generate_api_models_overview.py > docs/ARCHITECTURE/API_MODELS.md
python scripts/doc/generate_database_schema_overview.py > docs/ARCHITECTURE/DATABASE_SCHEMA.md
python scripts/doc/generate_configuration_overview.py > docs/ARCHITECTURE/CONFIGURATION.md
python scripts/doc/generate_repositories_overview.py > docs/ARCHITECTURE/REPOSITORIES.md
python scripts/doc/update_schemas_readme.py > schemas/README.md
python scripts/doc/generate_architecture_diagrams.py
python scripts/doc/generate_pngs.py
# python scripts/generate-doc-tree.py > docs/FILE-OVERVIEW.md
./scripts/generate-tree.sh
