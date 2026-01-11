./run-scc.sh
./count-words.sh
./run-coverage.sh
python scripts/update-coverage-stats.py
python scripts/doc/extract_endpoints.py > src/models/rest_api/ENDPOINTS.md
python scripts/generate_workers_overview.py > doc/ARCHITECTURE/WORKERS.md
python scripts/generate_services_overview.py > doc/ARCHITECTURE/SERVICES.md
python scripts/generate_api_models_overview.py > doc/ARCHITECTURE/API_MODELS.md
python scripts/generate_database_schema_overview.py > doc/ARCHITECTURE/DATABASE_SCHEMA.md
python scripts/generate_configuration_overview.py > doc/ARCHITECTURE/CONFIGURATION.md
python scripts/generate_repositories_overview.py > doc/ARCHITECTURE/REPOSITORIES.md
python scripts/generate_architecture_diagrams.py
python scripts/generate_pngs.py