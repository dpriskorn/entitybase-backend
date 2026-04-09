# Pydantic model_dump vs. json.dumps Analysis

This directory contains analysis and tests for handling JSON serialization in Pydantic models, particularly for logging data sizes.

## Background
In `statement_service.py`, we log `statement_data_size` for monitoring. Initially, `len(json.dumps(model.model_dump(mode="json")))` was used, but this includes spacing and may not reflect true byte size.

## Test Results
- `len(model.model_dump(mode="json"))`: Number of dict keys (e.g., 5 for a statement).
- `len(json.dumps(model.model_dump(mode="json")))`: JSON string length with default spacing (e.g., 317 chars).
- `len(model.model_dump_json())`: Compact JSON string length (e.g., 289 chars, no extra spaces).

## Conclusions
- For accurate "data size" logging, use `len(model.model_dump_json())` to get compact byte length.
- This avoids inflated sizes from `json.dumps` spacing and provides a true representation of stored data size.
- Applied to `statement_service.py` for `statement_data_size`.

## Usage
Run the test: `python test_len.py` (requires Pydantic in venv).
Output shows dict structure, key count, and various size metrics.