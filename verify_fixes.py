#!/usr/bin/env python3
"""Verification script for test fixes."""

import sys
sys.path.insert(0, 'src')

try:
    print("Testing EntityState field access...")
    from models.data.infrastructure.s3.entity_state import EntityState
    state = EntityState(is_semi_protected=True, is_locked=False, is_archived=True, is_dangling=False, is_mass_edit_protected=True)
    assert state.is_semi_protected is True
    assert state.is_locked is False
    assert state.is_archived is True
    assert state.is_dangling is False
    assert state.is_mass_edit_protected is True
    print("✓ EntityState field access works correctly")

    print("\nTesting EntityHashingService...")
    from models.rest_api.entitybase.v1.handlers.entity.entity_hashing_service import EntityHashingService
    print("✓ EntityHashingService imports successfully")

    print("\nTesting StatementService...")
    from models.rest_api.entitybase.v1.services.statement_service import StatementService
    print("✓ StatementService imports successfully")

    print("\nTesting PreparedRequestData...")
    from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
    data = {
        "id": "Q42",
        "type": "item",
        "labels": {},
        "descriptions": {},
        "claims": {},
        "aliases": {},
        "sitelinks": {},
        "forms": [],
        "senses": [],
    }
    prepared = PreparedRequestData(**data)
    print("✓ PreparedRequestData can be constructed from dict")

    print("\n✅ All verification checks passed!")
except Exception as e:
    print(f"\n❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
