"""Unit tests for BacklinkService."""

import pytest
from unittest.mock import MagicMock, AsyncMock


class TestBacklinkService:
    """Unit tests for BacklinkService."""

    def test_extract_backlinks_from_entity(self):
        """Test extracting backlinks from entity claims."""
        from models.rest_api.entitybase.v1.services.backlink_service import (
            BacklinkService,
        )
        from models.data.common import OperationResult

        mock_state = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.side_effect = lambda eid: {
            "Q1": 1,
            "Q2": 2,
            "Q5": 5,
        }.get(eid)
        mock_state.vitess_client.id_resolver = mock_id_resolver
        mock_state.vitess_client.backlink_repository = MagicMock()

        service = BacklinkService(state=mock_state)

        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "type": "wikibase-entityid",
                            "value": {"entity-type": "item", "id": "Q5"},
                        },
                    },
                    "rank": "normal",
                }
            ]
        }

        result = service.extract_backlinks_from_entity("Q1", claims)

        assert len(result) > 0
        assert any(r[0] == 5 for r in result)

    def test_extract_backlinks_empty_claims(self):
        """Test with empty claims returns empty list."""
        from models.rest_api.entitybase.v1.services.backlink_service import (
            BacklinkService,
        )

        mock_state = MagicMock()
        mock_state.vitess_client.id_resolver = MagicMock()
        mock_state.vitess_client.backlink_repository = MagicMock()

        service = BacklinkService(state=mock_state)

        result = service.extract_backlinks_from_entity("Q1", {})

        assert result == []

    def test_extract_backlinks_no_entity_references(self):
        """Test with non-entity statements (e.g., string values)."""
        from models.rest_api.entitybase.v1.services.backlink_service import (
            BacklinkService,
        )

        mock_state = MagicMock()
        mock_state.vitess_client.id_resolver = MagicMock()
        mock_state.vitess_client.backlink_repository = MagicMock()

        service = BacklinkService(state=mock_state)

        claims = {
            "P569": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P569",
                        "datavalue": {
                            "type": "time",
                            "value": {"time": "+2020-01-01T00:00:00Z"},
                        },
                    },
                    "rank": "normal",
                }
            ]
        }

        result = service.extract_backlinks_from_entity("Q1", claims)

        assert result == []

    def test_extract_backlinks_multiple_properties(self):
        """Test with multiple properties and statements."""
        from models.rest_api.entitybase.v1.services.backlink_service import (
            BacklinkService,
        )

        mock_state = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.side_effect = lambda eid: {
            "Q1": 1,
            "Q2": 2,
            "Q5": 5,
        }.get(eid)
        mock_state.vitess_client.id_resolver = mock_id_resolver
        mock_state.vitess_client.backlink_repository = MagicMock()

        service = BacklinkService(state=mock_state)

        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "type": "wikibase-entityid",
                            "value": {"entity-type": "item", "id": "Q5"},
                        },
                    },
                    "rank": "normal",
                }
            ],
            "P279": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P279",
                        "datavalue": {
                            "type": "wikibase-entityid",
                            "value": {"entity-type": "item", "id": "Q2"},
                        },
                    },
                    "rank": "preferred",
                }
            ],
        }

        result = service.extract_backlinks_from_entity("Q1", claims)

        assert len(result) == 2

    def test_extract_backlinks_unresolvable_entity(self):
        """Test handling of unresolvable entity IDs."""
        from models.rest_api.entitybase.v1.services.backlink_service import (
            BacklinkService,
        )

        mock_state = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.side_effect = lambda eid: None
        mock_state.vitess_client.id_resolver = mock_id_resolver
        mock_state.vitess_client.backlink_repository = MagicMock()

        service = BacklinkService(state=mock_state)

        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "type": "wikibase-entityid",
                            "value": {"entity-type": "item", "id": "Q999999"},
                        },
                    },
                    "rank": "normal",
                }
            ]
        }

        result = service.extract_backlinks_from_entity("Q1", claims)

        assert result == []

    def test_extract_and_store_backlinks_success(self):
        """Test successful extraction and storage."""
        from models.rest_api.entitybase.v1.services.backlink_service import (
            BacklinkService,
        )
        from models.data.common import OperationResult

        mock_state = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.side_effect = lambda eid: {"Q1": 1, "Q5": 5}.get(
            eid
        )
        mock_state.vitess_client.id_resolver = mock_id_resolver

        mock_repo = MagicMock()
        mock_repo.insert_backlinks.return_value = OperationResult(success=True)
        mock_state.vitess_client.backlink_repository = mock_repo

        service = BacklinkService(state=mock_state)

        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "type": "wikibase-entityid",
                            "value": {"entity-type": "item", "id": "Q5"},
                        },
                    },
                    "rank": "normal",
                }
            ]
        }

        result = service.extract_and_store_backlinks("Q1", claims)

        assert result.success is True
        mock_repo.insert_backlinks.assert_called_once()

    def test_extract_and_store_backlinks_no_backlinks(self):
        """Test when no backlinks found."""
        from models.rest_api.entitybase.v1.services.backlink_service import (
            BacklinkService,
        )
        from models.data.common import OperationResult

        mock_state = MagicMock()
        mock_state.vitess_client.id_resolver = MagicMock()
        mock_state.vitess_client.backlink_repository = MagicMock()

        service = BacklinkService(state=mock_state)

        result = service.extract_and_store_backlinks("Q1", {})

        assert result.success is True

    def test_extract_backlinks_with_qualifiers(self):
        """Test extracting backlinks from qualifiers."""
        from models.rest_api.entitybase.v1.services.backlink_service import (
            BacklinkService,
        )

        mock_state = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.side_effect = lambda eid: {
            "Q1": 1,
            "Q2": 2,
            "Q5": 5,
        }.get(eid)
        mock_state.vitess_client.id_resolver = mock_id_resolver
        mock_state.vitess_client.backlink_repository = MagicMock()

        service = BacklinkService(state=mock_state)

        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "type": "wikibase-entityid",
                            "value": {"entity-type": "item", "id": "Q5"},
                        },
                    },
                    "qualifiers": {
                        "P642": [
                            {
                                "snaktype": "value",
                                "property": "P642",
                                "datavalue": {
                                    "type": "wikibase-entityid",
                                    "value": {"entity-type": "item", "id": "Q2"},
                                },
                            }
                        ]
                    },
                    "qualifiers-order": ["P642"],
                    "rank": "normal",
                }
            ]
        }

        result = service.extract_backlinks_from_entity("Q1", claims)

        assert len(result) == 2
