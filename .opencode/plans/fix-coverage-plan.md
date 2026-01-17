# Plan to Fix Coverage XML Generation Issue

## Problem
The `run-coverage.sh` script runs pytest with coverage options, but `coverage.xml` is not found after execution, causing the script to skip the Python report generation.

## Root Cause Analysis
- Pytest with `--cov` and `--cov-report=xml` should generate `coverage.xml`, but it's not being created.
- Possible reasons:
  - Coverage data not collected due to import errors or test failures.
  - Command syntax issues (previously fixed the continuation line).
  - Path issues with PYTHONPATH or source directories.
  - Coverage plugin not generating XML when tests have errors.

## Proposed Solution
Replace the pytest --cov command with separate coverage run and coverage xml commands to ensure reliable coverage data collection and report generation.

### Changes to run-coverage.sh:
1. Replace:
   ```
   pytest \
     -m "unit" \
     --cov=src \
     --cov-report=term-missing \
     --cov-report=xml \
     > coverage.txt 2>&1
   ```
   
   With:
   ```
   coverage run --source=src -m pytest \
     -m "unit" \
     --cov-report=term-missing \
     > coverage.txt 2>&1
   coverage xml
   ```

### Benefits:
- `coverage run` collects coverage data reliably.
- `coverage xml` generates the XML report separately, ensuring it's created even if tests fail.
- Better separation of concerns.

### Risks:
- Requires `coverage` tool to be available (should be installed with pytest-cov).
- May change coverage behavior slightly if there are custom configurations.

## Implementation Steps
1. Edit `run-coverage.sh` to use `coverage run` and `coverage xml`.
2. Test the script to ensure `coverage.xml` is generated and the Python script runs.
3. Verify the coverage reports are correct.

## Verification
- Run `./run-coverage.sh` and check that `coverage.xml` exists.
- Ensure the Python script `scripts/generate_coverage_report.py` processes the XML correctly.
- Confirm coverage reports (term-missing, XML, and generated files) are accurate.