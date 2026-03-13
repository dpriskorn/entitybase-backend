"""Unit tests for S3 client lexeme term methods (lemma, form, sense)."""

from unittest.mock import MagicMock, patch

import pytest

from models.data.config.s3 import S3Config
from models.infrastructure.s3.client import MyS3Client


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

            client.vitess_metadata.store_lemma.assert_called_once_with(
                12345, "test lemma"
            )

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
            client.vitess_metadata.store_form_representation.return_value = MagicMock(
                success=True
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

    def test_store_lemma_not_configured(self):
        """Test store_lemma raises error when Vitess not configured."""
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
                client.store_lemma("test lemma", 12345)

    def test_store_lemma_failure(self):
        """Test store_lemma raises error when storage fails."""
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
            client.vitess_metadata.store_lemma.return_value = MagicMock(
                success=False, error="Database error"
            )

            with pytest.raises(Exception):
                client.store_lemma("test lemma", 12345)

    def test_store_form_representation_not_configured(self):
        """Test store_form_representation raises error when Vitess not configured."""
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
                client.store_form_representation("test form", 12345)

    def test_store_form_representation_failure(self):
        """Test store_form_representation raises error when storage fails."""
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
            client.vitess_metadata.store_form_representation.return_value = MagicMock(
                success=False, error="Database error"
            )

            with pytest.raises(Exception):
                client.store_form_representation("test form", 12345)

    def test_store_sense_gloss_not_configured(self):
        """Test store_sense_gloss raises error when Vitess not configured."""
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
                client.store_sense_gloss("test gloss", 12345)

    def test_store_sense_gloss_failure(self):
        """Test store_sense_gloss raises error when storage fails."""
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
                success=False, error="Database error"
            )

            with pytest.raises(Exception):
                client.store_sense_gloss("test gloss", 12345)

    def test_load_lemmas_batch_not_configured(self):
        """Test load_lemmas_batch raises error when Vitess not configured."""
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
                client.load_lemmas_batch([111, 222])

    def test_load_form_representations_batch_not_configured(self):
        """Test load_form_representations_batch raises error when Vitess not configured."""
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
                client.load_form_representations_batch([111, 222])

    def test_load_sense_glosses_batch_not_configured(self):
        """Test load_sense_glosses_batch raises error when Vitess not configured."""
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
                client.load_sense_glosses_batch([111, 222])
