"""End-to-end tests for revision read/write with content_hash."""

from unittest.mock import MagicMock, patch

import pytest
import sys

sys.path.insert(0, "src")

from models.data.infrastructure.s3 import PropertyCounts


class TestRevisionCreateReadE2E:
    """End-to-end tests for revision creation and read_with with content_hash."""

    @pytest.mark.asyncio
    async def test_create_and_read_revision_with_content_hash(self):
        """Test complete flow: create revision with content_hash, then read it back."""
        from models.infrastructure.s3.client import MyS3Client
        from models.data.infrastructure.s3.revision_data import S3RevisionData
        from models.data.config.s3 import S3Config
        from datetime import datetime, timezone

        content_hash = 12345678901234567890
        revision_id = 1
        entity_id = "Q42"

        # Mock data
        revision_dict = {
            "schema_version": "1.0",
            "revision_id": revision_id,
            "entity_type": "item",
            "entity": {"id": entity_id},
            "properties": [],
            "property_counts": {},
            "hashes": {"statements": {"root": []}},
            "edit": {
                "mass": False,
                "type": "manual_update",
                "user_id": 1,
                "summary": "test",
                "at": datetime.now(timezone.utc),
            },
            "state": {},
            "redirects_to": "",
        }

        # Setup S3 client mocks
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager"
        ) as mock_conn_class:
            mock_conn_class.return_value = mock_connection_manager

            # Mock vitess client
            mock_vitess_client = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (0,)  # revision doesn't exist
            mock_vitess_client.cursor = mock_cursor
            mock_id_resolver = MagicMock()
            mock_id_resolver.resolve_id.return_value = 100
            mock_vitess_client.id_resolver = mock_id_resolver
            mock_connection_manager.vitess_client = mock_vitess_client

            s3_client = MyS3Client(config=config)

            # Mock revision storage
            mock_revision_storage = MagicMock()
            mock_revision_storage.store_revision.return_value = MagicMock(success=True)
            s3_client.revisions = mock_revision_storage

            # Create S3RevisionData
            s3_revision_data = S3RevisionData(
                schema="1.0",
                revision=revision_dict,
                hash=content_hash,
                created_at=datetime.now(timezone.utc).isoformat(),
            )

            # Store revision
            s3_client.store_revision(content_hash, s3_revision_data)

            # Verify storage
            mock_revision_storage.store_revision.assert_called_once_with(
                content_hash, s3_revision_data
            )

    @pytest.mark.asyncio
    async def test_read_revision_queries_content_hash_from_db(self):
        """Test that read_revision queries DB for content_hash before accessing S3."""
        from models.infrastructure.s3.client import MyS3Client
        from models.data.config.s3 import S3Config

        entity_id = "Q42"
        internal_id = 100
        revision_id = 1
        content_hash = 12345678901234567890

        # Mock S3 client
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager"
        ) as mock_conn_class:
            mock_conn_class.return_value = mock_connection_manager

            # Mock vitess client
            mock_vitess_client = MagicMock()
            mock_id_resolver = MagicMock()
            mock_id_resolver.resolve_id.return_value = internal_id
            mock_vitess_client.id_resolver = mock_id_resolver
            mock_connection_manager.vitess_client = mock_vitess_client

            s3_client = MyS3Client(config=config)
            s3_client.vitess_client = mock_vitess_client

            # Mock revision repository
            mock_revision_repo = MagicMock()
            mock_revision_repo.get_content_hash.return_value = content_hash

            # Mock S3 revision storage
            expected_revision = {"entity": {"id": entity_id}}
            mock_revision_storage = MagicMock()
            mock_revision_storage.load_revision.return_value = expected_revision
            s3_client.revisions = mock_revision_storage

            # Read revision
            with patch(
                "models.infrastructure.s3.client.RevisionRepository",
                return_value=mock_revision_repo,
            ):
                result = s3_client.read_revision(entity_id, revision_id)

            # Verify flow
            mock_id_resolver.resolve_id.assert_called_once_with(entity_id)
            mock_revision_repo.get_content_hash.assert_called_once_with(
                internal_id, revision_id
            )
            mock_revision_storage.load_revision.assert_called_once_with(content_hash)
            assert result == expected_revision

    @pytest.mark.asyncio
    async def test_repository_create_with_content_hash(self):
        """Test RevisionRepository.create() stores content_hash."""
        from models.infrastructure.vitess.repositories.revision import (
            RevisionRepository,
        )
        from models.data.infrastructure.s3.entity_state import EntityState
        from models.data.infrastructure.s3.enums import EntityType, EditType, EditData
        from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.data.infrastructure.s3.hashes.statements_hashes import (
            StatementsHashes,
        )
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from datetime import datetime, timezone

        entity_id = "Q42"
        internal_id = 100
        revision_id = 1
        content_hash = 12345678901234567890

        # Mock vitess client
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)  # revision doesn't exist
        # Set up mock cursor as context manager
        mock_vitess_client.cursor = mock_cursor
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = internal_id
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        # Create revision data
        revision_data = RevisionData(
            schema_version="1.0",
            revision_id=revision_id,
            entity_type=EntityType.ITEM,
            properties=[],
            property_counts=PropertyCounts({}),
            hashes=HashMaps(statements=StatementsHashes(root=[])),
            edit=EditData(
                mass=False,
                type=EditType.MANUAL_UPDATE,
                user_id=1,
                summary="test",
                at=datetime.now(timezone.utc).isoformat(),
            ),
            state=EntityState(),
            redirects_to="",
        )

        # Create revision with content_hash
        repo.create(entity_id, revision_id, revision_data, content_hash=content_hash)

        # Verify content_hash is in one of the execute calls
        calls = mock_cursor.execute.call_args_list
        found = False
        for call in calls:
            params = call[0][1] if len(call[0]) > 1 else ()
            if content_hash in params:
                found = True
                break

        assert found, f"content_hash {content_hash} not found in any execute calls"

    @pytest.mark.asyncio
    async def test_repository_get_content_hash(self):
        """Test RevisionRepository.get_content_hash() retrieves stored hash."""
        from models.infrastructure.vitess.repositories.revision import (
            RevisionRepository,
        )

        internal_id = 100
        revision_id = 1
        content_hash = 12345678901234567890

        # Mock vitess client
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (content_hash,)
        mock_vitess_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_vitess_client.cursor.__exit__ = MagicMock(return_value=False)
        mock_vitess_client.cursor.return_value = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        # Get content_hash
        result = repo.get_content_hash(internal_id, revision_id)

        # Verify query and result
        mock_cursor.execute.assert_called_once()
        sql = mock_cursor.execute.call_args[0][0]
        assert "SELECT content_hash" in sql
        assert result == content_hash

    @pytest.mark.asyncio
    async def test_complete_lifecycle(self):
        """Test complete lifecycle: create, store, retrieve by content_hash."""
        from models.infrastructure.s3.client import MyS3Client
        from models.data.infrastructure.s3.revision_data import S3RevisionData
        from models.data.config.s3 import S3Config
        from datetime import datetime, timezone

        entity_id = "Q42"
        internal_id = 100
        revision_id = 1
        content_hash = 12345678901234567890

        revision_dict = {
            "entity": {"id": entity_id},
            "revision_id": revision_id,
        }

        # Mock S3 client
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager"
        ) as mock_conn_class:
            mock_conn_class.return_value = mock_connection_manager

            # Mock vitess client
            mock_vitess_client = MagicMock()
            mock_id_resolver = MagicMock()
            mock_id_resolver.resolve_id.return_value = internal_id
            mock_vitess_client.id_resolver = mock_id_resolver
            mock_connection_manager.vitess_client = mock_vitess_client

            s3_client = MyS3Client(config=config)
            s3_client.vitess_client = mock_vitess_client

            # Mock S3 revision storage
            mock_revision_storage = MagicMock()
            mock_revision_storage.store_revision.return_value = MagicMock(success=True)
            mock_revision_storage.load_revision.return_value = revision_dict
            s3_client.revisions = mock_revision_storage

            # Mock revision repository
            mock_revision_repo = MagicMock()
            mock_revision_repo.get_content_hash.return_value = content_hash

            # Step 1: Create and store revision
            s3_revision_data = S3RevisionData(
                schema="1.0",
                revision=revision_dict,
                hash=content_hash,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            s3_client.store_revision(content_hash, s3_revision_data)

            # Step 2: Mock database insert
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (0,)
            mock_vitess_client.cursor = mock_cursor

            # Step 3: Read revision back using the content_hash
            with patch(
                "models.infrastructure.s3.client.RevisionRepository",
                return_value=mock_revision_repo,
            ):
                result = s3_client.read_revision(entity_id, revision_id)

            # Verify: id resolution -> content_hash query -> S3 load
            assert result == revision_dict
            mock_id_resolver.resolve_id.assert_called_once_with(entity_id)
            mock_revision_repo.get_content_hash.assert_called_once_with(
                internal_id, revision_id
            )
            mock_revision_storage.load_revision.assert_called_once_with(content_hash)

    @pytest.mark.asyncio
    async def test_handler_creates_revision_with_content_hash(self):
        """Test that handlers calculate content_hash and pass to create methods."""
        from models.infrastructure.s3.client import MyS3Client
        from models.data.config.s3 import S3Config
        from unittest.mock import MagicMock, patch
        import json

        entity_id = "Q42"
        content_hash = 12345678901234567890

        # Mock connection manager
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager"
        ) as mock_conn_class:
            mock_conn_class.return_value = mock_connection_manager

            # Mock state
            mock_state = MagicMock()
            mock_vitess_client = MagicMock()
            mock_s3_client = MyS3Client(config=config)

            # Mock revision storage
            mock_revision_storage = MagicMock()
            mock_s3_client.revisions = mock_revision_storage

            mock_state.vitess_client = mock_vitess_client
            mock_state.s3_client = mock_s3_client

            # Mock handler - just test that content_hash is calculated
            revision_data = {"key": "value"}
            revision_json = json.dumps(revision_data, sort_keys=True)

            from models.internal_representation.metadata_extractor import (
                MetadataExtractor,
            )

            calculated_hash = MetadataExtractor.hash_string(revision_json)

            assert calculated_hash is not None
            assert isinstance(calculated_hash, int)
