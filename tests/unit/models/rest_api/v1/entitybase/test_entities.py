"""Unit tests for entities endpoints."""

from unittest.mock import MagicMock

import pytest


class TestEntitiesEndpoints:
    @pytest.fixture
    def mock_clients(self):
        clients = MagicMock()
        clients.vitess = MagicMock()
        clients.s3 = MagicMock()
        clients.stream_producer = MagicMock()
        clients.validator = MagicMock()
        return clients

    @pytest.fixture
    def mock_entity_response(self):
        response = MagicMock()
        response.entity_data = {
            "type": "item",
            "labels": {},
            "sitelinks": {"enwiki": {"title": "Old Page"}},
        }
        return response
