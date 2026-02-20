# JSON Dumps Linter - Allowlist Implementation

## Overview

The JSON dumps linter now includes an allowlist system to manage legitimate `json.dumps()` usage that shouldn't be flagged.

## Implementation Details

### Files Created/Modified

1. **Created:** `config/linters/allowlists/custom/json-dumps.txt`
   - Contains 15 allowlist entries for legitimate json.dumps() usage
   - Includes comments explaining each entry
   - Format: `filepath:line_number`

2. **Modified:** `run-json-lint.sh`
   - Updated to read and parse allowlist file
   - Filters out allowlisted entries from violations
   - Still correctly skips `model_dump(mode='json')` patterns

3. **Existing:** `run-linters.sh`
   - Already references `run-json-lint.sh`
   - No changes needed

## How It Works

### Allowlist Format
```
# Format: filepath:line_number
src/models/infrastructure/s3/base_storage.py:78
src/models/infrastructure/s3/client.py:76
```

### Linter Logic

1. Reads allowlist entries from `config/linters/allowlists/custom/json-dumps.txt`
2. Searches for all `json.dumps()` usage in Python files
3. Filters out:
   - Lines using `model_dump(mode='json')` (correct pattern)
   - Lines matching filepath:line_number in allowlist
4. Reports any remaining violations

### When to Add to Allowlist

Add entries when:
1. `json.dumps()` operates on a dict/list from proper `model_dump(mode='json')`
2. `json.dumps()` operates on simple dicts/lists that don't need special serialization
3. `json.dumps()` is used for canonical/hashing purposes with `sort_keys=True`

## Benefits

1. **No False Positives** - All 15 current legitimate uses are allowlisted
2. **Catches Real Issues** - Still flags problematic `model.model_dump()` patterns
3. **Maintainable** - Simple text file format with comments
4. **Documented** - Each entry explains why it's allowed
5. **Extensible** - Easy to add new entries as needed

## Usage

### Run Linter
```bash
./run-json-lint.sh
```

### Add New Allowlist Entry
If you get a false positive violation:
```bash
# Add to config/linters/allowlists/custom/json-dumps.txt
src/path/to/file.py:42  # Brief comment why
```

### View Current Allowlist
```bash
cat config/linters/allowlists/custom/json-dumps.txt
```

## Current Allowlist Summary

- **Total entries:** 15
- **Categories:**
  - Canonical/hashing (4): `*hasher.py`, `metadata_extractor.py`
  - Database serialization (4): `revision.py`, `user.py`, `backlink.py`
  - Revision data from `model_dump(mode='json')` (4): `client.py`, `handler.py`, `delete.py`, `revert.py`, `redirects.py`
  - Base storage fallback (1): `base_storage.py`

## Testing

The linter has been verified to:
1. Pass on the current codebase (no violations reported)
2. Correctly filter out allowlisted entries
3. Still catch problematic patterns (when they occur)
4. Provide clear error messages for violations

## Future Maintenance

- Remove entries if code is refactored
- Add entries for new legitimate uses
- Review allowlist periodically to ensure entries remain valid
- Consider refactoring code to reduce need for allowlist