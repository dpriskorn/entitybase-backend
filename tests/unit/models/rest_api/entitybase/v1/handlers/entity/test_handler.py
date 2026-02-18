"""Unit tests for EntityHandler."""

from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone
from typing import Any

import pytest

from models.data.infrastructure.s3.enums import EntityType, EditType
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.data.rest_api.v1.entitybase.request.entity.context import (
    ProcessEntityRevisionContext,
    RevisionContext,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
    StatementHashResult,
)
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.rest_api.entitybase.v1.handlers.entity.handler import (
    EntityHandler,
    RevisionResult,
)
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinkHashes


class TestEntityHandler:
    """Unit tests for EntityHandler."""

    @pytest.mark.asyncio
    async def test_build_revision_data_dangling_from_p6104(self) -> None:
        """Test _build_revision_data auto-computes is_dangling from P6104 claims."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        handler = EntityHandler(state=mock_state)

        request_data_no_p6104 = {
            "id": "Q42",
            "labels": {"en": {"language": "en", "value": "Test"}},
            "descriptions": {},
            "aliases": {},
            "claims": {"P31": [{"id": "Q1"}]},
        }

        ctx_no_p6104 = RevisionContext(
            entity_id="Q42",
            request_data=request_data_no_p6104,
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test",
            is_creation=True,
            vitess_client=mock_vitess,
            s3_client=mock_s3,
        )

        hash_result = StatementHashResult(
            statements=[123456789],
            properties=["P31"],
            property_counts={},
        )
        term_hashes = HashMaps(
            labels={"en": 123456789},
            descriptions={"en": 123456790},
            aliases={"en": [123456791]},
        )
        sitelink_hashes = SitelinkHashes(root={})

        revision_data_no_p6104 = handler._build_revision_data(
            ctx_no_p6104, hash_result, term_hashes, SitelinkHashes(root={}), 1
        )
        assert revision_data_no_p6104.state.is_dangling is True

        request_data_with_p6104 = {
            "id": "Q42",
            "labels": {"en": {"language": "en", "value": "Test"}},
            "descriptions": {},
            "aliases": {},
            "claims": {"P6104": [{"id": "Q123"}]},
        }

        ctx_with_p6104 = RevisionContext(
            entity_id="Q42",
            request_data=request_data_with_p6104,
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test",
            is_creation=True,
            vitess_client=mock_vitess,
            s3_client=mock_s3,
        )

        revision_data_with_p6104 = handler._build_revision_data(
            ctx_with_p6104, hash_result, term_hashes, SitelinkHashes(root={}), 1
        )
        assert revision_data_with_p6104.state.is_dangling is False

        request_data_empty_claims = {
            "id": "Q42",
            "labels": {},
            "descriptions": {},
            "aliases": {},
            "claims": {},
        }

        ctx_empty_claims = RevisionContext(
            entity_id="Q42",
            request_data=request_data_empty_claims,
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test",
            is_creation=True,
            vitess_client=mock_vitess,
            s3_client=mock_s3,
        )

        revision_data_empty_claims = handler._build_revision_data(
            ctx_empty_claims, hash_result, term_hashes, SitelinkHashes(root={}), 1
        )
        assert revision_data_empty_claims.state.is_dangling is True

    @pytest.mark.asyncio
    async def test_build_entity_response(self) -> None:
        """Test _build_entity_response method."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q42",
                "type": "item",
                "labels": {},
                "descriptions": {},
                "aliases": {},
                "claims": {},
                "sitelinks": {},
                "state": {
                    "is_semi_protected": False,
                    "is_locked": False,
                    "is_archived": False,
                    "is_dangling": False,
                    "is_mass_edit_protected": False,
                },
            },
            hash=123456789,
            created_at="2023-01-01T12:00:00Z",
        )

        mock_s3.read_revision.return_value = s3_revision_data

        entity_id = "Q42"
        result = RevisionResult(success=True, revision_id=1)

        ctx = RevisionContext(
            entity_id=entity_id,
            request_data={},
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test",
            is_creation=True,
            vitess_client=mock_vitess,
            s3_client=mock_s3,
        )

        response = await EntityHandler._build_entity_response(ctx, result)

        assert response.id == entity_id
        assert response.revision_id == 1
        assert isinstance(response.entity_data, S3RevisionData)

    @pytest.mark.asyncio
    async def test_build_entity_response_with_protection(self) -> None:
        """Test _build_entity_response with protection flags."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q42",
                "type": "item",
                "labels": {},
                "descriptions": {},
                "aliases": {},
                "claims": {},
                "sitelinks": {},
                "state": {
                    "is_semi_protected": True,
                    "is_locked": False,
                    "is_archived": True,
                    "is_dangling": False,
                    "is_mass_edit_protected": True,
                },
            },
            hash=123456789,
            created_at="2023-01-01T12:00:00Z",
        )

        mock_s3.read_revision.return_value = s3_revision_data

        entity_id = "Q42"
        result = RevisionResult(success=True, revision_id=1)

        ctx = RevisionContext(
            entity_id=entity_id,
            request_data={},
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test",
            is_creation=True,
            vitess_client=mock_vitess,
            s3_client=mock_s3,
        )

        response = await EntityHandler._build_entity_response(ctx, result)

        assert response.state.is_semi_protected is True
        assert response.state.is_locked is False
        assert response.state.is_archived is True
        assert response.state.is_dangling is False
        assert response.state.is_mass_edit_protected is True

    @pytest.mark.asyncio
    async def test_process_entity_data_new(self) -> None:
        """Test _process_entity_data_new method."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        handler = EntityHandler(state=mock_state)

        request_data = {
            "id": "Q42",
            "labels": {"en": {"language": "en", "value": "Test"}},
            "descriptions": {},
            "aliases": {},
            "sitelinks": {},
            "claims": {},
        }

        ctx = RevisionContext(
            entity_id="Q42",
            request_data=request_data,
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test",
            is_creation=True,
            vitess_client=mock_vitess,
            s3_client=mock_s3,
        )

        result = await handler._process_entity_data_new(ctx)

        assert isinstance(result, StatementHashResult)

    @pytest.mark.asyncio
    async def test_hash_terms_new(self) -> None:
        """Test _hash_terms_new method."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        handler = EntityHandler(state=mock_state)

        request_data = {
            "labels": {"en": {"language": "en", "value": "Test"}},
            "descriptions": {"en": {"language": "en", "value": "Test description"}},
            "aliases": {"en": [{"language": "en", "value": "Alias1"}]},
        }

        ctx = RevisionContext(
            entity_id="Q42",
            request_data=request_data,
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test",
            is_creation=True,
            vitess_client=mock_vitess,
            s3_client=mock_s3,
        )

        result = await handler._hash_terms_new(ctx)

        assert isinstance(result, HashMaps)
        assert hasattr(result, "labels")
        assert hasattr(result, "descriptions")
        assert hasattr(result, "aliases")

    @pytest.mark.asyncio
    async def test_hash_sitelinks_new(self) -> None:
        """Test _hash_sitelinks_new method."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        handler = EntityHandler(state=mock_state)

        request_data = {
            "sitelinks": {"enwiki": {"site": "enwiki", "title": "Test", "badges": []}}
        }

        ctx = RevisionContext(
            entity_id="Q42",
            request_data=request_data,
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test",
            is_creation=True,
            vitess_client=mock_vitess,
            s3_client=mock_s3,
        )

        result = await handler._hash_sitelinks_new(ctx)

        assert isinstance(result, SitelinkHashes)

    @pytest.mark.asyncio
    async def test_build_entity_response_s3_not_found(self) -> None:
        """Test _build_entity_response when S3 object not found (404)."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_s3.read_revision.side_effect = S3NotFoundError("Object not found: 123456")

        entity_id = "Q42"
        result = RevisionResult(success=True, revision_id=1)

        ctx = RevisionContext(
            entity_id=entity_id,
            request_data={},
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test",
            is_creation=True,
            vitess_client=mock_vitess,
            s3_client=mock_s3,
        )

        with pytest.raises(Exception):  # Should raise validation error with 404
            await EntityHandler._build_entity_response(ctx, result)
