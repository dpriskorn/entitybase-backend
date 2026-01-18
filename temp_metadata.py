import unittest
from unittest.mock import Mock, patch
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler


class TestEntityReadHandlerMetadata(unittest.TestCase):
    """Unit tests for EntityReadHandler metadata methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EntityReadHandler()
        self.mock_vitess = Mock()
