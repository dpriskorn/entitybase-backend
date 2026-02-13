"""Utility module for processing lexeme terms (forms and senses)."""

import logging
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field

from models.internal_representation.metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)


class TermProcessingConfig(BaseModel):
    """Configuration for processing lexeme term data."""

    model_config = {"extra": "forbid"}

    data_key: str = Field(..., description="Key for the data container")
    hash_key: str = Field(..., description="Key for hash storage")
    storage_method: str = Field(..., description="Name of S3 storage method")
    term_type: str = Field(..., description="Type of term for logging")


def process_lexeme_terms(
    forms: list[dict[str, Any]],
    senses: list[dict[str, Any]],
    s3_client: Any,
    lemmas: dict[str, dict[str, Any]] | None = None,
    on_form_stored: Optional[Callable[[int], None]] = None,
    on_gloss_stored: Optional[Callable[[int], None]] = None,
    on_lemma_stored: Optional[Callable[[int], None]] = None,
) -> None:
    """Process and deduplicate lexeme lemmas, form representations and sense glosses.

    Args:
        forms: List of form data with representations
        senses: List of sense data with glosses
        s3_client: S3 client instance for storage operations
        lemmas: Lexeme lemmas dict keyed by language
        on_form_stored: Optional callback for each stored form representation hash
        on_gloss_stored: Optional callback for each stored sense gloss hash
        on_lemma_stored: Optional callback for each stored lemma hash

    This function processes each term by:
    1. Hashing text value using MetadataExtractor
    2. Storing text in S3 with hash
    3. Adding hash to term data for deduplication
    4. Optionally invoking callbacks for each stored hash

    Errors during S3 storage are logged as warnings but don't halt processing.
    """
    logger.debug(
        f"Processing lexeme terms: {len(forms)} forms, {len(senses)} senses, {len(lemmas) if lemmas else 0} lemmas"
    )
    if not forms and not senses and not lemmas:
        logger.debug("No forms, senses, or lemmas to process")
        return

    logger.debug("Starting lemmas processing")
    if lemmas:
        lemmas_config = TermProcessingConfig(
            data_key="value",
            hash_key="lemma_hashes",
            storage_method="store_lemma",
            term_type="lemma",
        )

        _process_lexeme_lemmas(
            lemmas,
            s3_client,
            lemmas_config,
            on_lemma_stored,
        )

    logger.debug("Starting forms and senses processing")
    forms_config = TermProcessingConfig(
        data_key="representations",
        hash_key="representation_hashes",
        storage_method="store_form_representation",
        term_type="form representation",
    )

    _process_term_data(
        forms,
        s3_client,
        forms_config,
        on_form_stored,
    )

    senses_config = TermProcessingConfig(
        data_key="glosses",
        hash_key="gloss_hashes",
        storage_method="store_sense_gloss",
        term_type="sense gloss",
    )

    _process_term_data(
        senses,
        s3_client,
        senses_config,
        on_gloss_stored,
    )


def _process_lexeme_lemmas(
    lemmas: dict[str, dict[str, Any]],
    s3_client: Any,
    config: TermProcessingConfig,
    callback: Optional[Callable[[int], None]] = None,
) -> None:
    """Process lexeme lemmas dictionary.

    Args:
        lemmas: Dictionary of lemmas keyed by language
        s3_client: S3 client instance
        config: Processing configuration with data keys and storage method
        callback: Optional callback for each stored lemma hash

    Returns:
        None
    """
    extractor = MetadataExtractor()

    if "lemma_hashes" not in lemmas:
        lemmas["lemma_hashes"] = {}

    for lang, lemma_data in lemmas.items():
        if lang == "lemma_hashes":
            continue

        if "value" not in lemma_data:
            continue

        text = lemma_data["value"]
        hash_val = extractor.hash_string(text)
        lemmas["lemma_hashes"][lang] = hash_val

        try:
            storage_func = getattr(s3_client, config.storage_method)
            storage_func(text, hash_val)
            logger.debug(f"Stored {config.term_type} hash {hash_val}")
            if callback is not None:
                callback(hash_val)
        except Exception as e:
            logger.warning(f"Failed to store {config.term_type}: {e}")


def _process_term_data(
    terms: list[dict[str, Any]],
    s3_client: Any,
    config: TermProcessingConfig,
    callback: Optional[Callable[[int], None]] = None,
) -> None:
    """Process a list of term data (forms or senses) with given keys.

    Args:
        terms: List of term dictionaries
        s3_client: S3 client instance
        config: Processing configuration with data keys and storage method
        callback: Optional callback for each stored hash

    Returns:
        None
    """
    extractor = MetadataExtractor()

    for term in terms:
        if config.data_key not in term:
            continue

        if config.hash_key not in term:
            term[config.hash_key] = {}

        for lang, term_data in term[config.data_key].items():
            if "value" not in term_data:
                continue

            text = term_data["value"]
            hash_val = extractor.hash_string(text)
            term[config.hash_key][lang] = hash_val

            try:
                storage_func = getattr(s3_client, config.storage_method)
                storage_func(text, hash_val)
                logger.debug(f"Stored {config.term_type} hash {hash_val}")
                if callback is not None:
                    callback(hash_val)
            except Exception as e:
                logger.warning(f"Failed to store {config.term_type}: {e}")
