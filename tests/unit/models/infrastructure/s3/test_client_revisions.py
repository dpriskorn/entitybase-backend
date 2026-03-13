"""Unit tests for S3 client revision methods."""

from unittest.mock import MagicMock, patch

import pytest

from models.data.config.s3 import S3Config
from models.data.infrastructure.s3 import S3RevisionData
from models.infrastructure.s3.client import MyS3Client


class TestS3ClientRevisions:
    """Unit tests for S3 client revision methods."""

    def test_store_revision_success(self) -> None:
        """Test successful revision storage via S3 client."""
        # Create a mock S3 client
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)

            # Mock the revision storage
            mock_revision_storage = MagicMock()
            client.revisions = mock_revision_storage
            mock_revision_storage.store_revision.return_value = MagicMock(success=True)

            # Test data
            revision_data = S3RevisionData(
                schema="1.0.0",
                revision={"entity": {"id": "Q42"}},
                hash=12345,
                created_at="2023-01-01T12:00:00Z",
            )

            # Call the method
            client.store_revision(12345, revision_data)

            # Verify the storage was called
            mock_revision_storage.store_revision.assert_called_once_with(
                12345, revision_data
            )

    def test_load_revision_success(self) -> None:
        """Test successful revision loading via S3 client."""
        # Create a mock S3 client
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)

            # Mock the revision storage
            mock_revision_storage = MagicMock()
            client.revisions = mock_revision_storage

            expected_revision_data = S3RevisionData(
                schema="1.0.0",
                revision={"entity": {"id": "Q42"}},
                hash=12345,
                created_at="2023-01-01T12:00:00Z",
            )
            mock_revision_storage.load_revision.return_value = expected_revision_data

            # Call the method
            result = client.load_revision(12345)

            # Verify the result
            assert result == expected_revision_data
            mock_revision_storage.load_revision.assert_called_once_with(12345)

    def test_read_revision_with_content_hash(self):
        """Test read_revision queries content_hash and loads from S3."""
        # Create a mock S3 client
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        # Mock vitess client and id_resolver
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.id_resolver = mock_id_resolver

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config, vitess_client=mock_vitess_client)

            # Mock revision repository
            mock_revision_repo = MagicMock()
            mock_revision_repo.get_content_hash.return_value = 12345678901234567890

            # Mock revision storage
            mock_revision_storage = MagicMock()
            expected_revision_data = {"entity": {"id": "Q42"}}
            mock_revision_storage.load_revision.return_value = expected_revision_data
            client.revisions = mock_revision_storage

            # Call read_revision
            with patch(
                "models.infrastructure.s3.client.RevisionRepository",
                return_value=mock_revision_repo,
            ):
                result = client.read_revision("Q42", 1)

            # Verify
            assert result == expected_revision_data
            mock_id_resolver.resolve_id.assert_called_once_with("Q42")
            mock_revision_repo.get_content_hash.assert_called_once_with(123, 1)
            mock_revision_storage.load_revision.assert_called_once_with(
                12345678901234567890
            )

    def test_read_revision_entity_not_found(self):
        """Test read_revision raises 404 when entity not found."""
        # Create a mock S3 client
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        # Mock vitess client with entity not found
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config, vitess_client=mock_vitess_client)

            # Call read_revision and expect error
            with pytest.raises(Exception):
                client.read_revision("Q999", 1)

    def test_read_revision_revision_not_found(self):
        """Test read_revision raises 404 when revision not found."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.id_resolver = mock_id_resolver

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config, vitess_client=mock_vitess_client)

            mock_revision_repo = MagicMock()
            mock_revision_repo.get_content_hash.return_value = 0

            with patch(
                "models.infrastructure.s3.client.RevisionRepository",
                return_value=mock_revision_repo,
            ):
                with pytest.raises(Exception):
                    client.read_revision("Q42", 999)


class TestS3ClientStatements:
    """Unit tests for S3 client statement methods."""

    def test_delete_statement_success(self):
        """Test successful statement deletion."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_statements = MagicMock()
            client.vitess_statements.delete_statement.return_value = MagicMock(
                success=True
            )

            client.delete_statement(12345)

            client.vitess_statements.delete_statement.assert_called_once_with(12345)

    def test_delete_statement_not_configured(self):
        """Test delete_statement raises error when Vitess not configured."""
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=MagicMock(),
        ):
            client = MyS3Client(config=config)

            with pytest.raises(Exception):
                client.delete_statement(12345)

    def test_write_statement_success(self):
        """Test successful statement write."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_statements = MagicMock()
            client.vitess_statements.store_statement.return_value = MagicMock(
                success=True
            )

            client.write_statement(
                12345, {"statement": {"id": "Q1"}}, "1.0.0"
            )

            client.vitess_statements.store_statement.assert_called_once()

    def test_read_statement_success(self):
        """Test successful statement read."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_statements = MagicMock()
            client.vitess_statements.load_statement.return_value = {"id": "statement1"}

            result = client.read_statement(12345)

            assert result == {"id": "statement1"}

    def test_read_statement_not_found(self):
        """Test read_statement raises error when not found."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_statements = MagicMock()
            client.vitess_statements.load_statement.return_value = None

            with pytest.raises(Exception):
                client.read_statement(12345)


class TestS3ClientMetadata:
    """Unit tests for S3 client metadata methods."""

    def test_store_term_metadata_success(self):
        """Test successful term metadata storage."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.store_metadata.return_value = MagicMock(success=True)

            client.store_term_metadata("Test", 12345, "labels")

            client.vitess_metadata.store_metadata.assert_called_once()

    def test_load_metadata_success(self):
        """Test successful metadata load."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.load_metadata.return_value = "Test value"

            from models.data.infrastructure.s3.enums import MetadataType

            result = client.load_metadata(MetadataType.LABELS, 12345)

            assert result is not None
            assert result.data == "Test value"

    def test_load_metadata_not_found(self):
        """Test load_metadata returns None when not found."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.load_metadata.return_value = None

            from models.data.infrastructure.s3.enums import MetadataType

            result = client.load_metadata(MetadataType.LABELS, 12345)

            assert result is None

    def test_store_sitelink_metadata_success(self):
        """Test successful sitelink metadata storage."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_sitelinks = MagicMock()
            client.vitess_sitelinks.store_sitelink.return_value = MagicMock(success=True)

            client.store_sitelink_metadata("Main_Page", 12345)

            client.vitess_sitelinks.store_sitelink.assert_called_once()

    def test_load_sitelink_metadata_success(self):
        """Test successful sitelink metadata load."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_sitelinks = MagicMock()
            client.vitess_sitelinks.load_sitelink.return_value = "Main_Page"

            result = client.load_sitelink_metadata(12345)

            assert result == "Main_Page"

    def test_load_sitelink_metadata_not_found(self):
        """Test load_sitelink_metadata raises error when not found."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_sitelinks = MagicMock()
            client.vitess_sitelinks.load_sitelink.return_value = None

            with pytest.raises(Exception):
                client.load_sitelink_metadata(12345)

    def test_delete_metadata_success(self):
        """Test successful metadata deletion."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.delete_metadata.return_value = MagicMock(success=True)

            from models.data.infrastructure.s3.enums import MetadataType

            client.delete_metadata(MetadataType.LABELS, 12345)

            client.vitess_metadata.delete_metadata.assert_called_once()


class TestS3ClientReferences:
    """Unit tests for S3 client reference methods."""

    def test_store_reference_success(self):
        """Test successful reference storage."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_references = MagicMock()
            client.vitess_references.store_reference.return_value = MagicMock(
                success=True
            )

            from models.data.infrastructure.s3.reference_data import S3ReferenceData

            ref_data = S3ReferenceData(reference={"id": "ref1"}, hash=12345, created_at="2023-01-01T12:00:00Z")
            client.store_reference(12345, ref_data)

            client.vitess_references.store_reference.assert_called_once()

    def test_load_reference_success(self):
        """Test successful reference load."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_references = MagicMock()
            from models.data.infrastructure.s3.reference_data import S3ReferenceData

            client.vitess_references.load_reference.return_value = S3ReferenceData(
                reference={"id": "ref1"}, hash=12345, created_at="2023-01-01T12:00:00Z"
            )

            result = client.load_reference(12345)

            assert result.content_hash == 12345

    def test_load_references_batch(self):
        """Test loading references batch."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_references = MagicMock()
            client.vitess_references.load_references_batch.return_value = [
                None,
                {"id": "ref2"},
            ]

            result = client.load_references_batch([111, 222])

            assert len(result) == 2
            assert result[0] is None


class TestS3ClientQualifiers:
    """Unit tests for S3 client qualifier methods."""

    def test_store_qualifier_success(self):
        """Test successful qualifier storage."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_qualifiers = MagicMock()
            client.vitess_qualifiers.store_qualifier.return_value = MagicMock(
                success=True
            )

            from models.data.infrastructure.s3.qualifier_data import S3QualifierData

            qual_data = S3QualifierData(qualifier={"id": "q1"}, hash=12345, created_at="2023-01-01T12:00:00Z")
            client.store_qualifier(12345, qual_data)

            client.vitess_qualifiers.store_qualifier.assert_called_once()

    def test_load_qualifier_success(self):
        """Test successful qualifier load."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_qualifiers = MagicMock()
            from models.data.infrastructure.s3.qualifier_data import S3QualifierData

            client.vitess_qualifiers.load_qualifier.return_value = S3QualifierData(
                qualifier={"id": "q1"}, hash=12345, created_at="2023-01-01T12:00:00Z"
            )

            result = client.load_qualifier(12345)

            assert result.content_hash == 12345

    def test_load_qualifiers_batch(self):
        """Test loading qualifiers batch."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_qualifiers = MagicMock()
            client.vitess_qualifiers.load_qualifiers_batch.return_value = [
                None,
                {"id": "q2"},
            ]

            result = client.load_qualifiers_batch([111, 222])

            assert len(result) == 2


class TestS3ClientSnaks:
    """Unit tests for S3 client snak methods."""

    def test_store_snak_success(self):
        """Test successful snak storage."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_snaks = MagicMock()
            client.vitess_snaks.store_snak.return_value = MagicMock(success=True)

            from models.data.infrastructure.s3.snak_data import S3SnakData

            snak_data = S3SnakData(snak={"id": "s1"}, hash=12345, schema="1.0.0", created_at="2023-01-01T12:00:00Z")
            client.store_snak(12345, snak_data)

            client.vitess_snaks.store_snak.assert_called_once()

    def test_load_snak_success(self):
        """Test successful snak load."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_snaks = MagicMock()
            from models.data.infrastructure.s3.snak_data import S3SnakData

            client.vitess_snaks.load_snak.return_value = S3SnakData(
                snak={"id": "s1"}, hash=12345, schema="1.0.0", created_at="2023-01-01T12:00:00Z"
            )

            result = client.load_snak(12345)

            assert result.content_hash == 12345

    def test_load_snaks_batch(self):
        """Test loading snaks batch."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_snaks = MagicMock()
            client.vitess_snaks.load_snaks_batch.return_value = [None, {"id": "s2"}]

            result = client.load_snaks_batch([111, 222])

            assert len(result) == 2


class TestS3ClientLexemeTerms:
    """Unit tests for S3 client lexeme term methods (lemma, form, sense)."""

    def test_store_lemma_success(self):
        """Test successful lemma storage."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.store_lemma.return_value = MagicMock(success=True)

            client.store_lemma("test lemma", 12345)

            client.vitess_metadata.store_lemma.assert_called_once_with(12345, "test lemma")

    def test_store_form_representation_success(self):
        """Test successful form representation storage."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.store_form_representation.return_value = (
                MagicMock(success=True)
            )

            client.store_form_representation("test form", 12345)

            client.vitess_metadata.store_form_representation.assert_called_once()

    def test_store_sense_gloss_success(self):
        """Test successful sense gloss storage."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.store_sense_gloss.return_value = MagicMock(
                success=True
            )

            client.store_sense_gloss("test gloss", 12345)

            client.vitess_metadata.store_sense_gloss.assert_called_once()

    def test_load_lemmas_batch(self):
        """Test loading lemmas batch."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.load_lemmas_batch.return_value = [
                "lemma1",
                "lemma2",
            ]

            result = client.load_lemmas_batch([111, 222])

            assert result == ["lemma1", "lemma2"]

    def test_load_form_representations_batch(self):
        """Test loading form representations batch."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.load_form_representations_batch.return_value = [
                "form1",
                "form2",
            ]

            result = client.load_form_representations_batch([111, 222])

            assert result == ["form1", "form2"]

    def test_load_sense_glosses_batch(self):
        """Test loading sense glosses batch."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_metadata = MagicMock()
            client.vitess_metadata.load_sense_glosses_batch.return_value = [
                "gloss1",
                "gloss2",
            ]

            result = client.load_sense_glosses_batch([111, 222])

            assert result == ["gloss1", "gloss2"]


class TestS3ClientDisconnect:
    """Unit tests for S3 client disconnect."""

    def test_disconnect(self):
        """Test disconnect clears connection."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            mock_connection_manager.boto_client = "some_client"

            client.disconnect()

            assert mock_connection_manager.boto_client is None
