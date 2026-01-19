from unittest.mock import Mock, patch
from models.rest_api.entitybase.handlers.entity.handler import EntityHandler
from models.rest_api.entitybase.response.statement import StatementHashResult


class TestBacklinkPopulation:
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.handler = EntityHandler()
        self.vitess_client = Mock()
        self.s3_client = Mock()
        self.validator = Mock()

    @patch(
        "models.rest_api.entitybase.services.statement_service.hash_entity_statements"
    )
    @patch(
        "models.rest_api.entitybase.services.statement_service.deduplicate_and_store_statements"
    )
    def test_backlink_population_creation_success(
        self, mock_dedup: Mock, mock_hash: Mock
    ) -> None:
        """Test successful backlink population during entity creation."""
        entity_id = "Q123"
        request_data = {
            "id": entity_id,
            "type": "item",
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datavalue": {
                                "value": {"entity-type": "item", "id": "Q5"},
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "normal",
                    }
                ]
            },
        }

        # Mock hash result
        mock_hash_result = StatementHashResult(
            statements=[12345],
            properties=["P31"],
            property_counts={"P31": 1},
            full_statements=[
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                }
            ],
        )
        mock_hash.return_value = mock_hash_result

        # Mock connection and resolver
        mock_conn = Mock()
        self.vitess_client.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        self.vitess_client.id_resolver.resolve_id.return_value = (
            999  # internal_id for Q123
        )
        self.vitess_client.id_resolver.resolve_id.side_effect = lambda conn, eid: {
            "Q123": 999,
            "Q5": 555,
        }.get(eid, 0)

        result = self.handler.process_statements(
            entity_id, request_data, self.vitess_client, self.s3_client, self.validator
        )

        # Verify hash was called
        mock_hash.assert_called_once_with(request_data)

        # Verify deduplication was called
        mock_dedup.assert_called_once()

        # Verify backlink population
        self.vitess_client.backlink_repository.delete_backlinks_for_entity.assert_called_once_with(
            mock_conn, 999
        )
        self.vitess_client.insert_backlinks.assert_called_once_with(
            [(555, 999, 12345, "P31", "normal")]
        )

        assert result == mock_hash_result

    @patch(
        "models.rest_api.entitybase.services.statement_service.hash_entity_statements"
    )
    @patch(
        "models.rest_api.entitybase.services.statement_service.deduplicate_and_store_statements"
    )
    def test_backlink_population_no_statements(
        self, mock_dedup: Mock, mock_hash: Mock
    ) -> None:
        """Test backlink population when entity has no statements."""
        entity_id = "Q123"
        request_data = {"id": entity_id, "type": "item", "claims": {}}

        mock_hash_result = StatementHashResult()
        mock_hash.return_value = mock_hash_result

        result = self.handler.process_statements(
            entity_id, request_data, self.vitess_client, self.s3_client, self.validator
        )

        # Should not attempt backlink operations
        self.vitess_client.connection_manager.get_connection.assert_not_called()
        self.vitess_client.backlink_repository.delete_backlinks_for_entity.assert_not_called()
        self.vitess_client.insert_backlinks.assert_not_called()

        assert result == mock_hash_result

    @patch(
        "models.rest_api.entitybase.services.statement_service.hash_entity_statements"
    )
    @patch(
        "models.rest_api.entitybase.services.statement_service.deduplicate_and_store_statements"
    )
    def test_backlink_population_entity_not_found(
        self, mock_dedup: Mock, mock_hash: Mock
    ) -> None:
        """Test backlink population when entity internal_id cannot be resolved."""
        entity_id = "Q123"
        request_data = {
            "id": entity_id,
            "type": "item",
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datavalue": {
                                "value": {"entity-type": "item", "id": "Q5"},
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "normal",
                    }
                ]
            },
        }

        mock_hash_result = StatementHashResult(
            statements=[12345],
            properties=["P31"],
            property_counts={"P31": 1},
            full_statements=[
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                }
            ],
        )
        mock_hash.return_value = mock_hash_result

        # Mock connection and resolver - entity not found
        mock_conn = Mock()
        self.vitess_client.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        self.vitess_client.id_resolver.resolve_id.return_value = 0  # not found

        result = self.handler.process_statements(
            entity_id, request_data, self.vitess_client, self.s3_client, self.validator
        )

        # Should not attempt backlink operations
        self.vitess_client.backlink_repository.delete_backlinks_for_entity.assert_not_called()
        self.vitess_client.insert_backlinks.assert_not_called()

        assert result == mock_hash_result

    @patch(
        "models.rest_api.entitybase.services.statement_service.hash_entity_statements"
    )
    @patch(
        "models.rest_api.entitybase.services.statement_service.deduplicate_and_store_statements"
    )
    def test_backlink_population_referenced_entity_not_found(
        self, mock_dedup: Mock, mock_hash: Mock
    ) -> None:
        """Test backlink population when referenced entity cannot be resolved."""
        entity_id = "Q123"
        request_data = {
            "id": entity_id,
            "type": "item",
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datavalue": {
                                "value": {
                                    "entity-type": "item",
                                    "id": "Q999",
                                },  # non-existent
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "normal",
                    }
                ]
            },
        }

        mock_hash_result = StatementHashResult(
            statements=[12345],
            properties=["P31"],
            property_counts={"P31": 1},
            full_statements=[
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q999"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                }
            ],
        )
        mock_hash.return_value = mock_hash_result

        # Mock connection and resolver
        mock_conn = Mock()
        self.vitess_client.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        self.vitess_client.id_resolver.resolve_id.side_effect = lambda conn, eid: {
            "Q123": 999,
            "Q999": 0,  # not found
        }.get(eid, 0)

        result = self.handler.process_statements(
            entity_id, request_data, self.vitess_client, self.s3_client, self.validator
        )

        # Should delete existing backlinks but insert empty list (since referenced not found)
        self.vitess_client.backlink_repository.delete_backlinks_for_entity.assert_called_once_with(
            mock_conn, 999
        )
        self.vitess_client.insert_backlinks.assert_called_once_with(
            []
        )  # empty because referenced not resolvable

        assert result == mock_hash_result

    @patch(
        "models.rest_api.entitybase.services.statement_service.hash_entity_statements"
    )
    def test_backlink_population_multiple_statements(
        self, mock_hash: Mock
    ) -> None:
        """Test backlink population with multiple statements and references."""
        entity_id = "Q123"
        request_data = {
            "id": entity_id,
            "type": "item",
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datavalue": {
                                "value": {"entity-type": "item", "id": "Q5"},
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "normal",
                        "qualifiers": {
                            "P580": [
                                {
                                    "snaktype": "value",
                                    "property": "P580",
                                    "datavalue": {
                                        "value": {"entity-type": "item", "id": "Q10"},
                                        "type": "wikibase-entityid",
                                    },
                                }
                            ]
                        },
                    }
                ],
                "P17": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P17",
                            "datavalue": {
                                "value": {"entity-type": "item", "id": "Q20"},
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "preferred",
                    }
                ],
            },
        }

        mock_hash_result = StatementHashResult(
            statements=[12345, 67890],
            properties=["P31", "P17"],
            property_counts={"P31": 1, "P17": 1},
            full_statements=[
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {
                        "P580": [
                            {
                                "snaktype": "value",
                                "property": "P580",
                                "datavalue": {
                                    "value": {"entity-type": "item", "id": "Q10"},
                                    "type": "wikibase-entityid",
                                },
                            }
                        ]
                    },
                },
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P17",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q20"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "preferred",
                },
            ],
        )
        mock_hash.return_value = mock_hash_result

        # Mock connection and resolver
        mock_conn = Mock()
        self.vitess_client.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        self.vitess_client.id_resolver.resolve_id.side_effect = lambda conn, eid: {
            "Q123": 999,
            "Q5": 555,
            "Q10": 1010,
            "Q20": 2020,
        }.get(eid, 0)

        result = self.handler.process_statements(
            entity_id, request_data, self.vitess_client, self.s3_client, self.validator
        )

        # Verify multiple backlinks inserted
        expected_backlinks = [
            (555, 999, 12345, "P31", "normal"),  # mainsnak
            (1010, 999, 12345, "P580", "normal"),  # qualifier
            (2020, 999, 67890, "P17", "preferred"),  # second statement
        ]
        self.vitess_client.insert_backlinks.assert_called_once_with(expected_backlinks)

        assert result == mock_hash_result
