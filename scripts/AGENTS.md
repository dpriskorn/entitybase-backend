# Shell Scripts Organization

This document explains how shell scripts are organized and used in this project.

## Directory Structure

All shell scripts are located in `scripts/shell/`:

```
scripts/shell/
├── run-ruff.sh           # Individual linter/test scripts
├── run-mypy.sh
├── run-unit-01-config-data.sh
├── ...
├── update-docs.sh       # Documentation generation
└── stop-docker-and-remove-everything.sh
```

Shell scripts that live in other `scripts/` subdirectories (e.g., `scripts/linters/`, `scripts/download/`) are **not** moved - they stay in place.

## Script Structure

All scripts in `scripts/shell/` include a line to change to the project root directory:

```bash
#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

# Script content here...
```

This allows scripts to be run from any working directory while still referencing paths relative to the project root.

## Makefile Integration

The `Makefile` delegates to scripts in `scripts/shell/`:

```makefile
ruff:
	./scripts/shell/run-ruff.sh

test-unit-01:
	./scripts/shell/run-unit-01-config-data.sh

docs:
	./scripts/shell/update-docs.sh
```

Run `make help` to see all available targets.

## Running Scripts Directly

Scripts can be run directly without make:

```bash
./scripts/shell/run-ruff.sh
./scripts/shell/run-unit-01-config-data.sh
```

## Adding a New Shell Script

1. Create the script in `scripts/shell/` (not in the project root)
2. Add the directory change line after the shebang:
   ```bash
   #!/bin/bash
   cd "$(dirname "$0")/../.."
   set -Eeuo pipefail
   ```
3. Add a corresponding target in the `Makefile` (or update an existing one)
4. Test with `make <target>` or directly `./scripts/shell/<script>.sh`

## Documentation Scripts

The `update-docs.sh` script generates documentation by calling other scripts and Python tools:

```bash
./scripts/shell/run-scc.sh                  # Code statistics
./scripts/shell/count-tests.sh              # Test counts
./scripts/shell/count-words.sh              # Word counts
python scripts/doc/extract_endpoints.py     # API endpoints
python scripts/doc/generate_*.py            # Various architecture docs
```

Run with `make docs`.
