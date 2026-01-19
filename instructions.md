# Error Handling Instructions

## Validation Error Raising

**Always use `raise_validation_error()` instead of raising `ValidationError` directly** to ensure proper HTTP error handling for user responses.

- In production: Raises `HTTPException` with appropriate status code
- In development/test: Raises `ValueError` for easier debugging

This provides suitable HTTP responses (4xx status codes) while maintaining debuggability in development environments.

### Example Usage

```python
from models.rest_api.utils import raise_validation_error

# Good: HTTP-aware error handling
raise_validation_error("Invalid input data", status_code=400)

# Bad: Direct ValidationError (no HTTP response handling)
raise ValidationError("Invalid input data")
```

### Repository Code

Repository methods should always use `raise_validation_error` for input validation:

```python
def insert_backlink_statistics(self, conn, date, total_backlinks, ...):
    if not isinstance(date, str) or len(date) != 10:
        raise_validation_error(f"Invalid date format: {date}. Expected YYYY-MM-DD", status_code=400)
```

### Test Code

Tests should expect the appropriate exception based on environment:

```python
# For repository validation errors, expect ValueError in tests
with pytest.raises(ValueError):
    repository.some_method(invalid_data)
```