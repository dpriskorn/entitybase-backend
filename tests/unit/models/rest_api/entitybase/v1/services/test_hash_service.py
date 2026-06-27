"""Unit tests for HashService."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinkHashes
from models.data.infrastructure.s3.hashes.labels_hashes import LabelsHashes
from models.data.infrastructure.s3.hashes.descriptions_hashes import DescriptionsHashes
from models.data.infrastructure.s3.hashes.aliases_hashes import AliasesHashes
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.s3.sitelink_data import S3SitelinkData
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.rest_api.entitybase.v1.services.hash_service import HashService


class TestHashService:
    """Unit tests for HashService."""

    def test_hash_sitelinks(self):
        """Test hashing sitelinks with badges."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        service = HashService(state=state)

        sitelinks = {
            "enwiki": {"title": "Test Page", "badges": ["featured"]},
            "dewiki": {"title": "Test Seite", "badges": []},
        }

        with patch(
            "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string",
            side_effect=lambda x: hash(x),
        ):
            result = service.hash_sitelinks(sitelinks)

            assert isinstance(result, SitelinkHashes)
            assert "enwiki" in result.root
            assert isinstance(result.root["enwiki"], S3SitelinkData)
            assert result.root["enwiki"].title_hash == hash("Test Page")
            assert result.root["enwiki"].badges == ["featured"]
            assert result.root["dewiki"].title_hash == hash("Test Seite")
            assert result.root["dewiki"].badges == []

            s3_client.store_sitelink_metadata.assert_any_call(
                "Test Page", hash("Test Page")
            )
            s3_client.store_sitelink_metadata.assert_any_call(
                "Test Seite", hash("Test Seite")
            )

    def test_hash_sitelinks_no_title(self):
        """Test hashing sitelinks skips entries without title."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        service = HashService(state=state)

        sitelinks = {
            "enwiki": {"badges": ["featured"]},
            "dewiki": {"title": "Test Seite", "badges": []},
        }

        with patch(
            "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string",
            side_effect=lambda x: hash(x),
        ):
            result = service.hash_sitelinks(sitelinks)

            assert "enwiki" not in result.root
            assert "dewiki" in result.root
            assert result.root["dewiki"].title_hash == hash("Test Seite")

    def test_hash_sitelinks_empty(self):
        """Test hashing empty sitelinks dict."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        service = HashService(state=state)

        result = service.hash_sitelinks({})

        assert isinstance(result, SitelinkHashes)
        assert len(result.root) == 0

    def test_hash_statements_success(self):
        """Test hashing statements successfully."""
        state = MagicMock()
        service = HashService(state=state)

        mock_hash_result = MagicMock()
        mock_hash_result.success = True
        mock_hash_result.get_data.return_value = MagicMock(statements=[123, 456])

        mock_store_result = MagicMock()
        mock_store_result.success = True

        with patch(
            "models.rest_api.entitybase.v1.services.hash_service.StatementService"
        ) as MockStatementService:
            mock_ss_instance = MockStatementService.return_value
            mock_ss_instance.hash_entity_statements.return_value = mock_hash_result
            mock_ss_instance.deduplicate_and_store_statements.return_value = (
                mock_store_result
            )

            mock_entity_data = MagicMock(spec=PreparedRequestData)
            result = service.hash_statements(mock_entity_data)

            assert isinstance(result, StatementsHashes)
            assert result.root == [123, 456]
            mock_ss_instance.hash_entity_statements.assert_called_once_with(
                mock_entity_data
            )
            mock_ss_instance.deduplicate_and_store_statements.assert_called_once()

    def test_hash_statements_hash_failure(self):
        """Test hashing statements when hashing fails."""
        state = MagicMock()
        service = HashService(state=state)

        mock_hash_result = MagicMock()
        mock_hash_result.success = False
        mock_hash_result.error = "Hashing error"

        with patch(
            "models.rest_api.entitybase.v1.services.hash_service.StatementService"
        ) as MockStatementService:
            mock_ss_instance = MockStatementService.return_value
            mock_ss_instance.hash_entity_statements.return_value = mock_hash_result

            mock_entity_data = MagicMock(spec=PreparedRequestData)
            with pytest.raises(HTTPException) as exc_info:
                service.hash_statements(mock_entity_data)

            assert exc_info.value.status_code == 500
            assert "Failed to hash statements" in str(exc_info.value.detail)

    def test_hash_statements_store_failure(self):
        """Test hashing statements when store fails."""
        state = MagicMock()
        service = HashService(state=state)

        mock_hash_result = MagicMock()
        mock_hash_result.success = True
        mock_hash_result.get_data.return_value = MagicMock(statements=[123, 456])

        mock_store_result = MagicMock()
        mock_store_result.success = False
        mock_store_result.error = "Storage error"

        with patch(
            "models.rest_api.entitybase.v1.services.hash_service.StatementService"
        ) as MockStatementService:
            mock_ss_instance = MockStatementService.return_value
            mock_ss_instance.hash_entity_statements.return_value = mock_hash_result
            mock_ss_instance.deduplicate_and_store_statements.return_value = (
                mock_store_result
            )

            mock_entity_data = MagicMock(spec=PreparedRequestData)
            with pytest.raises(HTTPException) as exc_info:
                service.hash_statements(mock_entity_data)

            assert exc_info.value.status_code == 500
            assert "Failed to store statements" in str(exc_info.value.detail)

    def test_hash_labels_with_mysql_config(self):
        """Test hashing labels with mysql_config enabled."""
        state = MagicMock()
        s3_client = MagicMock()
        mysql_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = MagicMock()
        state.mysql_client = mysql_client

        mock_insert_result = MagicMock()
        mock_insert_result.success = True
        mock_insert_result.error = ""

        with patch(
            "models.rest_api.entitybase.v1.services.hash_service.TermsRepository"
        ) as MockTermsRepo:
            mock_terms_repo_instance = MockTermsRepo.return_value
            mock_terms_repo_instance.insert_term.return_value = mock_insert_result

            service = HashService(state=state)

            labels = {
                "en": {"value": "Test Label"},
                "de": {"value": "German Label"},
            }

            with patch(
                "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string",
                side_effect=lambda x: hash(x),
            ):
                result = service.hash_labels(labels)

                assert "en" in result.root
                assert "de" in result.root
                assert result.root["en"] == hash("Test Label")
                assert result.root["de"] == hash("German Label")

                s3_client.store_term_metadata.assert_called()
                mock_terms_repo_instance.insert_term.assert_called()

    def test_hash_labels_without_mysql_config(self):
        """Test hashing labels when mysql_config is None returns empty."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = None

        service = HashService(state=state)

        labels = {"en": {"value": "Test Label"}}

        result = service.hash_labels(labels)

        assert isinstance(result, LabelsHashes)
        assert len(result.root) == 0

    def test_hash_labels_no_value_key(self):
        """Test hashing labels skips entries without value key."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = MagicMock()
        mysql_client = MagicMock()
        state.mysql_client = mysql_client

        with patch(
            "models.rest_api.entitybase.v1.services.hash_service.TermsRepository"
        ) as MockTermsRepo:
            mock_terms_repo_instance = MockTermsRepo.return_value

            service = HashService(state=state)

            labels = {"en": {"language": "en"}}

            with patch(
                "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string",
                side_effect=lambda x: hash(x),
            ):
                result = service.hash_labels(labels)

                assert "en" not in result.root

    def test_hash_descriptions_with_mysql_config(self):
        """Test hashing descriptions with mysql_config enabled."""
        state = MagicMock()
        s3_client = MagicMock()
        mysql_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = MagicMock()
        state.mysql_client = mysql_client

        mock_insert_result = MagicMock()
        mock_insert_result.success = True
        mock_insert_result.error = ""

        with patch(
            "models.rest_api.entitybase.v1.services.hash_service.TermsRepository"
        ) as MockTermsRepo:
            mock_terms_repo_instance = MockTermsRepo.return_value
            mock_terms_repo_instance.insert_term.return_value = mock_insert_result

            service = HashService(state=state)

            descriptions = {"en": {"value": "Test Description"}}

            with patch(
                "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string",
                side_effect=lambda x: hash(x),
            ):
                result = service.hash_descriptions(descriptions)

                assert "en" in result.root
                s3_client.store_term_metadata.assert_called()
                mock_terms_repo_instance.insert_term.assert_called()

    def test_hash_descriptions_without_mysql_config(self):
        """Test hashing descriptions when mysql_config is None returns empty."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = None

        service = HashService(state=state)

        descriptions = {"en": {"value": "Test Description"}}

        result = service.hash_descriptions(descriptions)

        assert isinstance(result, DescriptionsHashes)
        assert len(result.root) == 0

    def test_hash_descriptions_no_value_key(self):
        """Test hashing descriptions skips entries without value key."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = MagicMock()
        mysql_client = MagicMock()
        state.mysql_client = mysql_client

        with patch(
            "models.rest_api.entitybase.v1.services.hash_service.TermsRepository"
        ) as MockTermsRepo:
            mock_terms_repo_instance = MockTermsRepo.return_value

            service = HashService(state=state)

            descriptions = {"en": {"language": "en"}}

            with patch(
                "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string",
                side_effect=lambda x: hash(x),
            ):
                result = service.hash_descriptions(descriptions)

                assert "en" not in result.root

    def test_hash_aliases_with_mysql_config(self):
        """Test hashing aliases with mysql_config enabled."""
        state = MagicMock()
        s3_client = MagicMock()
        mysql_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = MagicMock()
        state.mysql_client = mysql_client

        mock_insert_result = MagicMock()
        mock_insert_result.success = True
        mock_insert_result.error = ""

        with patch(
            "models.rest_api.entitybase.v1.services.hash_service.TermsRepository"
        ) as MockTermsRepo:
            mock_terms_repo_instance = MockTermsRepo.return_value
            mock_terms_repo_instance.insert_term.return_value = mock_insert_result

            service = HashService(state=state)

            aliases = {"en": [{"value": "Alias1"}, {"value": "Alias2"}]}

            with patch(
                "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string",
                side_effect=lambda x: hash(x),
            ):
                result = service.hash_aliases(aliases)

                assert "en" in result.root
                assert len(result.root["en"]) == 2
                s3_client.store_term_metadata.assert_called()

    def test_hash_aliases_without_mysql_config(self):
        """Test hashing aliases when mysql_config is None returns empty."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = None

        service = HashService(state=state)

        aliases = {"en": [{"value": "Alias1"}]}

        result = service.hash_aliases(aliases)

        assert isinstance(result, AliasesHashes)
        assert len(result.root) == 0

    def test_hash_aliases_no_value_key(self):
        """Test hashing aliases skips entries without value key."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = MagicMock()
        mysql_client = MagicMock()
        state.mysql_client = mysql_client

        with patch(
            "models.rest_api.entitybase.v1.services.hash_service.TermsRepository"
        ) as MockTermsRepo:
            mock_terms_repo_instance = MockTermsRepo.return_value

            service = HashService(state=state)

            aliases = {"en": [{"language": "en"}]}

            with patch(
                "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string",
                side_effect=lambda x: hash(x),
            ):
                result = service.hash_aliases(aliases)

                assert "en" in result.root
                assert len(result.root["en"]) == 0

    def test_hash_entity_metadata_full(self):
        """Test hashing all entity metadata."""
        state = MagicMock()
        s3_client = MagicMock()
        mysql_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = MagicMock()
        state.mysql_client = mysql_client

        mock_insert_result = MagicMock()
        mock_insert_result.success = True
        mock_insert_result.error = ""

        mock_hash_result = MagicMock()
        mock_hash_result.success = True
        mock_hash_result.get_data.return_value = MagicMock(statements=[123])

        mock_store_result = MagicMock()
        mock_store_result.success = True

        entity_data = MagicMock()
        entity_data.claims = {"P1": [{"mainsnak": {}}]}
        entity_data.get.side_effect = lambda k, d=None: {
            "sitelinks": {"enwiki": {"title": "Test"}},
            "labels": {"en": {"value": "Label"}},
            "descriptions": {"en": {"value": "Desc"}},
            "aliases": {"en": [{"value": "Alias"}]},
        }.get(k, d)

        with (
            patch(
                "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string",
                side_effect=lambda x: hash(x),
            ),
            patch(
                "models.rest_api.entitybase.v1.services.hash_service.StatementService"
            ) as MockStatementService,
            patch(
                "models.rest_api.entitybase.v1.services.hash_service.TermsRepository"
            ) as MockTermsRepo,
        ):
            mock_ss_instance = MockStatementService.return_value
            mock_ss_instance.hash_entity_statements.return_value = mock_hash_result
            mock_ss_instance.deduplicate_and_store_statements.return_value = (
                mock_store_result
            )

            mock_terms_repo_instance = MockTermsRepo.return_value
            mock_terms_repo_instance.insert_term.return_value = mock_insert_result

            service = HashService(state=state)

            result = service.hash_entity_metadata(entity_data)

            assert result.statements is not None
            assert result.sitelinks is not None
            assert result.labels is not None
            assert result.descriptions is not None
            assert result.aliases is not None

    def test_hash_entity_metadata_empty_sitelinks(self):
        """Test hashing entity metadata with no sitelinks."""
        state = MagicMock()
        s3_client = MagicMock()
        mysql_client = MagicMock()
        state.s3_client = s3_client
        state.mysql_config = MagicMock()
        state.mysql_client = mysql_client

        mock_insert_result = MagicMock()
        mock_insert_result.success = True
        mock_insert_result.error = ""

        mock_hash_result = MagicMock()
        mock_hash_result.success = True
        mock_hash_result.get_data.return_value = MagicMock(statements=[])

        mock_store_result = MagicMock()
        mock_store_result.success = True

        entity_data = MagicMock()
        entity_data.claims = {}
        entity_data.get.side_effect = lambda k, d=None: {
            "sitelinks": {},
            "labels": {},
            "descriptions": {},
            "aliases": {},
        }.get(k, d)

        with (
            patch(
                "models.rest_api.entitybase.v1.services.hash_service.StatementService"
            ) as MockStatementService,
            patch(
                "models.rest_api.entitybase.v1.services.hash_service.TermsRepository"
            ) as MockTermsRepo,
        ):
            mock_ss_instance = MockStatementService.return_value
            mock_ss_instance.hash_entity_statements.return_value = mock_hash_result
            mock_ss_instance.deduplicate_and_store_statements.return_value = (
                mock_store_result
            )

            mock_terms_repo_instance = MockTermsRepo.return_value
            mock_terms_repo_instance.insert_term.return_value = mock_insert_result

            service = HashService(state=state)

            result = service.hash_entity_metadata(entity_data)

            assert result.statements is not None
            assert len(result.sitelinks.root) == 0
