"""Unit tests for redirects service."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest
from models.data.rest_api.v1.entitybase.response import EntityRedirectResponse
from models.data.rest_api.v1.entitybase.response import EntityRevertResponse
from models.rest_api.entitybase.v1.services.redirects import RedirectService


# Import classes that need to be mocked


class TestRedirectService:
    """Unit tests for RedirectService."""
    pass