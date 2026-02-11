"""Unit tests for entities revision endpoints."""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from models.rest_api.entitybase.v1.endpoints.entities import (
    get_entity_json_revision,
    get_entity_ttl_revision,
)
from models.data.infrastructure.s3 import S3RevisionData
from models.infrastructure.s3.exceptions import S3NotFoundError


class TestEntityTTLRevisionEndpoint:
    """Test the TTL revision endpoint."""

    @pytest.mark.asyncio
    async def test_get_entity_ttl_revision_success(self, mock_entity_read_state):
        """Test getting TTL revision data successfully."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q123",
                "labels": {"en": {"language": "en", "value": "Test"}},
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with patch.object(RDFSerializer, "entity_data_to_rdf") as mock_serialize:
            mock_serialize.return_value = "@prefix wd: <http://example.com/> ."

            result = await get_entity_ttl_revision(
                req=mock_req, entity_id="Q123", revision_id=1, format_="turtle"
            )

            assert result.status_code == 200
            assert result.media_type == "text/turtle"
            mock_s3.read_revision.assert_called_once_with("Q123", 1)
            mock_serialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_entity_ttl_revision_s3_not_found(self, mock_entity_read_state):
        """Test getting TTL revision when S3 content is not found."""
        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_s3.read_revision.side_effect = S3NotFoundError("Object not found: 123456")

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await get_entity_ttl_revision(
                req=mock_req, entity_id="Q123", revision_id=1, format_="turtle"
            )

        assert exc.value.status_code == 404
        assert "Revision content not found" in exc.value.detail

    @pytest.mark.asyncio
    async def test_get_entity_ttl_revision_different_formats(
        self, mock_entity_read_state
    ):
        """Test getting TTL revision with different format options."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q123",
                "labels": {"en": {"language": "en", "value": "Test"}},
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        formats_and_content_types = {
            "turtle": "text/turtle",
            "rdfxml": "application/rdf+xml",
            "ntriples": "application/n-triples",
        }

        for format_, expected_content_type in formats_and_content_types.items():
            with patch.object(RDFSerializer, "entity_data_to_rdf") as mock_serialize:
                mock_serialize.return_value = "mocked rdf content"

                result = await get_entity_ttl_revision(
                    req=mock_req, entity_id="Q123", revision_id=1, format_=format_
                )

                assert result.status_code == 200
                assert expected_content_type in result.media_type


class TestEntityJsonRevisionEndpoint:
    """Test the JSON revision endpoint."""

    @pytest.mark.asyncio
    async def test_get_entity_json_revision_success(self, mock_entity_read_state):
        """Test getting JSON revision data successfully."""
        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q123",
                "labels": {"en": {"language": "en", "value": "Test"}},
                "claims": {},
            },
            hash=123456,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_entity_json_revision(
            entity_id="Q123", revision_id=1, req=mock_req
        )

        assert result.data["id"] == "Q123"
        assert result.data["labels"]["en"]["value"] == "Test"
        mock_s3.read_revision.assert_called_once_with("Q123", 1)

    @pytest.mark.asyncio
    async def test_get_entity_json_revision_s3_not_found(self, mock_entity_read_state):
        """Test getting JSON revision when S3 content is not found."""
        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_s3.read_revision.side_effect = S3NotFoundError("Object not found: 123456")

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        with pytest.raises(HTTPException) as exc:
            await get_entity_json_revision(
                entity_id="Q123", revision_id=1, req=mock_req
            )

        assert exc.value.status_code == 404
        assert "Revision content not found" in exc.value.detail

    @pytest.mark.asyncio
    async def test_get_entity_json_revision_with_complex_data(
        self, mock_entity_read_state
    ):
        """Test getting JSON revision with complex entity data."""
        mock_state, mock_vitess, mock_s3 = mock_entity_read_state

        mock_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q456",
                "labels": {
                    "en": {"language": "en", "value": "English Label"},
                    "fr": {"language": "fr", "value": "French Label"},
                },
                "descriptions": {
                    "en": {"language": "en", "value": "English Description"}
                },
                "claims": {
                    "P31": [
                        {
                            "mainsnak": {
                                "datatype": "wikibase-item",
                                "datavalue": {
                                    "value": {"entity-type": "item", "id": "Q5"},
                                    "type": "wikibase-entityid",
                                },
                                "property": "P31",
                                "snaktype": "value",
                            },
                            "type": "statement",
                            "id": "Q456$1",
                        }
                    ]
                },
            },
            hash=789012,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = mock_revision_data

        mock_req = Mock()
        mock_req.app.state.state_handler = mock_state

        result = await get_entity_json_revision(
            entity_id="Q456", revision_id=2, req=mock_req
        )

        assert result.data["id"] == "Q456"
        assert "en" in result.data["labels"]
        assert "fr" in result.data["labels"]
        assert "P31" in result.data["claims"]
        assert len(result.data["claims"]["P31"]) == 1
