#!/usr/bin/env python
"""Simple test script to verify implementation."""
import sys
sys.path.insert(0, "src")

from models.data.rest_api.v1.entitybase.request.entity_filter import EntityFilterRequest

filter_request = EntityFilterRequest(
    entity_type="item",
    status="locked",
    limit=10,
    offset=0
)

print("EntityFilterRequest created successfully:")
print(filter_request.model_dump_json(indent=2))
