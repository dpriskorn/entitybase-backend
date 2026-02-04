#!/usr/bin/env python
"""Quick verification script for EditHeaders."""

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from pydantic import ValidationError

# Test the exact case from the question
try:
    edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")
    print("✓ Basic instantiation works: EditHeaders(x_user_id=123, x_edit_summary='test')")
    print(f"  - x_user_id: {edit_headers.x_user_id}")
    print(f"  - x_edit_summary: {edit_headers.x_edit_summary}")
except Exception as e:
    print(f"✗ Basic instantiation failed: {e}")

# Test edge cases
print("\n--- Testing edge cases ---")

# Test minimum user_id (0)
try:
    edit_headers = EditHeaders(x_user_id=0, x_edit_summary="System")
    print("✓ Minimum user_id (0) works")
except Exception as e:
    print(f"✗ Minimum user_id failed: {e}")

# Test negative user_id (should fail)
try:
    edit_headers = EditHeaders(x_user_id=-1, x_edit_summary="test")
    print("✗ Negative user_id should have failed validation")
except ValidationError:
    print("✓ Negative user_id correctly raises ValidationError")

# Test empty summary (should fail)
try:
    edit_headers = EditHeaders(x_user_id=123, x_edit_summary="")
    print("✗ Empty summary should have failed validation")
except ValidationError:
    print("✓ Empty summary correctly raises ValidationError")

# Test minimum summary length
try:
    edit_headers = EditHeaders(x_user_id=123, x_edit_summary="x")
    print("✓ Minimum summary length (1 char) works")
except Exception as e:
    print(f"✗ Minimum summary length failed: {e}")

# Test maximum summary length
try:
    edit_headers = EditHeaders(x_user_id=123, x_edit_summary="a" * 200)
    print("✓ Maximum summary length (200 chars) works")
except Exception as e:
    print(f"✗ Maximum summary length failed: {e}")

# Test too long summary (should fail)
try:
    edit_headers = EditHeaders(x_user_id=123, x_edit_summary="a" * 201)
    print("✗ Too long summary should have failed validation")
except ValidationError:
    print("✓ Too long summary correctly raises ValidationError")

# Test aliases
try:
    edit_headers = EditHeaders(X_User_ID=999, X_Edit_Summary="Alias test")
    print("✓ Alias instantiation works: EditHeaders(X_User_ID=999, X_Edit_Summary='Alias test')")
    print(f"  - x_user_id: {edit_headers.x_user_id}")
    print(f"  - x_edit_summary: {edit_headers.x_edit_summary}")
except Exception as e:
    print(f"✗ Alias instantiation failed: {e}")

# Test model_dump
try:
    edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")
    dumped = edit_headers.model_dump()
    print(f"✓ model_dump() works: {dumped}")
except Exception as e:
    print(f"✗ model_dump() failed: {e}")

# Test model_dump with by_alias
try:
    edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")
    dumped = edit_headers.model_dump(by_alias=True)
    print(f"✓ model_dump(by_alias=True) works: {dumped}")
except Exception as e:
    print(f"✗ model_dump(by_alias=True) failed: {e}")

print("\n--- All tests completed ---")
