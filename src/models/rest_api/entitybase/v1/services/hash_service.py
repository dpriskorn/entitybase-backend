"""Hash service for entity metadata processing."""

import logging
from typing import Any

from models.data.infrastructure.s3.hashes.aliases_hashes import AliasesHashes
from models.data.infrastructure.s3.hashes.descriptions_hashes import DescriptionsHashes
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.labels_hashes import LabelsHashes
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinksHashes
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes

from models.infrastructure.vitess.repositories.terms import TermsRepository
from models.internal_representation.metadata_extractor import MetadataExtractor
from models.rest_api.entitybase.v1.service import Service
from models.rest_api.entitybase.v1.services.statement_service import StatementService
from models.validation.json_schema_validator import JsonSchemaValidator

logger = logging.getLogger(__name__)


# noinspection PyArgumentList
class HashService(Service):
    """Service for hashing entity metadata components."""

    def hash_statements(
        self,
        entity_data: dict[str, Any],
        validator: JsonSchemaValidator | None = None,
    ) -> StatementsHashes:
        """Hash statements from entity data."""
        ss = StatementService(state=self.state)
        hash_result = ss.hash_entity_statements(entity_data)
        if not hash_result.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(
                f"Failed to hash statements: {hash_result.error}", status_code=500
            )

        # Deduplicate and store
        assert hash_result.data is not None  # Guaranteed by success check above
        store_result = ss.deduplicate_and_store_statements(
            hash_result.data,
            validator,
        )
        if not store_result.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(
                f"Failed to store statements: {store_result.error}", status_code=500
            )

        return StatementsHashes(root=hash_result.data.statements)

    def hash_sitelinks(
        self,
        sitelinks: dict[str, Any],
    ) -> SitelinksHashes:
        """Hash sitelink titles and store in S3."""
        hashes = {}
        for wiki, sitelink_data in sitelinks.items():
            if "title" in sitelink_data:
                title = sitelink_data["title"]
                hash_value = MetadataExtractor.hash_string(title)
                hashes[wiki] = hash_value
                self.state.s3_client.store_sitelink_metadata(title, hash_value)
        return SitelinksHashes(root=hashes)

    def hash_labels(
        self,
        labels: dict[str, Any],
    ) -> LabelsHashes:
        """Hash label values, store in S3 and Vitess."""
        hashes = {}
        if self.state.vitess_config:
            terms_repo = TermsRepository(vitess_client=self.vitess_client)
            for lang, label_data in labels.items():
                if "value" in label_data:
                    value = label_data["value"]
                    hash_value = MetadataExtractor.hash_string(value)
                    hashes[lang] = hash_value
                    self.state.s3_client.store_term_metadata(value, hash_value)
                    terms_repo.insert_term(hash_value, value, "label")
        return LabelsHashes(root=hashes)

    def hash_descriptions(
        self,
        descriptions: dict[str, Any],
    ) -> DescriptionsHashes:
        """Hash description values, store in S3 and Vitess."""
        hashes = {}
        if self.state.vitess_config:
            terms_repo = TermsRepository(vitess_client=self.vitess_client)
            for lang, desc_data in descriptions.items():
                if "value" in desc_data:
                    value = desc_data["value"]
                    hash_value = MetadataExtractor.hash_string(value)
                    hashes[lang] = hash_value
                    self.state.s3_client.store_term_metadata(value, hash_value)
                    terms_repo.insert_term(hash_value, value, "description")
        return DescriptionsHashes(root=hashes)

    def hash_aliases(
        self,
        aliases: dict[str, Any],
    ) -> AliasesHashes:
        """Hash alias values, store in S3 and Vitess."""
        hashes = {}
        if self.state.vitess_config:
            terms_repo = TermsRepository(vitess_client=self.vitess_client)
            for lang, alias_list in aliases.items():
                lang_hashes = []
                for alias_data in alias_list:
                    if "value" in alias_data:
                        value = alias_data["value"]
                        hash_value = MetadataExtractor.hash_string(value)
                        lang_hashes.append(hash_value)
                        self.state.s3_client.store_term_metadata(value, hash_value)
                        terms_repo.insert_term(hash_value, value, "alias")
                hashes[lang] = lang_hashes
        return AliasesHashes(root=hashes)

    def hash_entity_metadata(
        self,
        entity_data: dict[str, Any],
        validator: JsonSchemaValidator | None = None,
    ) -> HashMaps:
        """Hash all entity metadata and return HashMaps."""
        statements_hashes = self.hash_statements(entity_data, validator)

        sitelinks = entity_data.get("sitelinks", {})
        sitelinks_hashes = self.hash_sitelinks(sitelinks)

        labels = entity_data.get("labels", {})
        labels_hashes = self.hash_labels(labels)

        descriptions = entity_data.get("descriptions", {})
        descriptions_hashes = self.hash_descriptions(descriptions)

        aliases = entity_data.get("aliases", {})
        aliases_hashes = self.hash_aliases(aliases)

        return HashMaps(
            statements=statements_hashes,
            sitelinks=sitelinks_hashes,
            labels=labels_hashes,
            descriptions=descriptions_hashes,
            aliases=aliases_hashes,
        )
