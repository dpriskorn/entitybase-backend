"""Hash service for entity metadata processing."""

import logging
from typing import Any

from models.infrastructure.s3.hashes.hash_maps import (
    HashMaps,
    AliasesHashes,
    DescriptionsHashes,
    LabelsHashes,
    SitelinksHashes,
    StatementsHashes,
)
from models.infrastructure.s3.client import MyS3Client
from models.infrastructure.vitess.client import VitessClient
from models.internal_representation.metadata_extractor import MetadataExtractor
from models.infrastructure.vitess.repositories.terms import TermsRepository
from models.rest_api.entitybase.v1.services.statement_service import (
    hash_entity_statements,
    deduplicate_and_store_statements,
)
from models.validation.json_schema_validator import JsonSchemaValidator

logger = logging.getLogger(__name__)


# noinspection PyArgumentList
class HashService:
    """Service for hashing entity metadata components."""

    @staticmethod
    def hash_statements(
        entity_data: dict[str, Any],
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        validator: JsonSchemaValidator | None = None,
    ) -> StatementsHashes:
        """Hash statements from entity data."""
        hash_result = hash_entity_statements(entity_data)
        if not hash_result.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(
                f"Failed to hash statements: {hash_result.error}", status_code=500
            )

        # Deduplicate and store
        assert hash_result.data is not None  # Guaranteed by success check above
        store_result = deduplicate_and_store_statements(
            hash_result.data,
            vitess_client,
            s3_client,
            validator,
        )
        if not store_result.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(
                f"Failed to store statements: {store_result.error}", status_code=500
            )

        return StatementsHashes(root=hash_result.data.statements)

    @staticmethod
    def hash_sitelinks(
        sitelinks: dict[str, Any],
        s3_client: MyS3Client,
    ) -> SitelinksHashes:
        """Hash sitelink titles and store in S3."""
        hashes = {}
        for wiki, sitelink_data in sitelinks.items():
            if "title" in sitelink_data:
                title = sitelink_data["title"]
                hash_value = MetadataExtractor.hash_string(title)
                hashes[wiki] = hash_value
                s3_client.store_sitelink_metadata(title, hash_value)
        return SitelinksHashes(root=hashes)

    @staticmethod
    def hash_labels(
        labels: dict[str, Any],
        s3_client: MyS3Client,
        vitess_client: VitessClient,
    ) -> LabelsHashes:
        """Hash label values, store in S3 and Vitess."""
        hashes = {}
        terms_repo = TermsRepository(vitess_client.connection_manager)
        for lang, label_data in labels.items():
            if "value" in label_data:
                value = label_data["value"]
                hash_value = MetadataExtractor.hash_string(value)
                hashes[lang] = hash_value
                s3_client.store_term_metadata(value, hash_value)
                terms_repo.insert_term(hash_value, value, "label")
        return LabelsHashes(root=hashes)

    @staticmethod
    def hash_descriptions(
        descriptions: dict[str, Any],
        s3_client: MyS3Client,
        vitess_client: VitessClient,
    ) -> DescriptionsHashes:
        """Hash description values, store in S3 and Vitess."""
        hashes = {}
        terms_repo = TermsRepository(vitess_client.connection_manager)
        for lang, desc_data in descriptions.items():
            if "value" in desc_data:
                value = desc_data["value"]
                hash_value = MetadataExtractor.hash_string(value)
                hashes[lang] = hash_value
                s3_client.store_term_metadata(value, hash_value)
                terms_repo.insert_term(hash_value, value, "description")
        return DescriptionsHashes(root=hashes)

    @staticmethod
    def hash_aliases(
        aliases: dict[str, Any],
        s3_client: MyS3Client,
        vitess_client: VitessClient,
    ) -> AliasesHashes:
        """Hash alias values, store in S3 and Vitess."""
        hashes = {}
        terms_repo = TermsRepository(vitess_client.connection_manager)
        for lang, alias_list in aliases.items():
            lang_hashes = []
            for alias_data in alias_list:
                if "value" in alias_data:
                    value = alias_data["value"]
                    hash_value = MetadataExtractor.hash_string(value)
                    lang_hashes.append(hash_value)
                    s3_client.store_term_metadata(value, hash_value)
                    terms_repo.insert_term(hash_value, value, "alias")
            hashes[lang] = lang_hashes
        return AliasesHashes(root=hashes)

    @staticmethod
    def hash_entity_metadata(
        entity_data: dict[str, Any],
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        validator: JsonSchemaValidator | None = None,
    ) -> HashMaps:
        """Hash all entity metadata and return HashMaps."""
        statements_hashes = HashService.hash_statements(
            entity_data,  validator
        )

        sitelinks = entity_data.get("sitelinks", {})
        sitelinks_hashes = HashService.hash_sitelinks(sitelinks, s3_client)

        labels = entity_data.get("labels", {})
        labels_hashes = HashService.hash_labels(labels, s3_client)

        descriptions = entity_data.get("descriptions", {})
        descriptions_hashes = HashService.hash_descriptions(
            descriptions, s3_client
        )

        aliases = entity_data.get("aliases", {})
        aliases_hashes = HashService.hash_aliases(aliases, s3_client)

        return HashMaps(
            statements=statements_hashes,
            sitelinks=sitelinks_hashes,
            labels=labels_hashes,
            descriptions=descriptions_hashes,
            aliases=aliases_hashes,
        )
