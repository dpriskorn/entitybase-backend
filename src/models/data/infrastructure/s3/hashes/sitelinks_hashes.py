"""Sitelinks hashes model."""

from pydantic.root_model import RootModel

from models.data.infrastructure.s3.sitelink_data import S3SitelinkData


class SitelinkHashes(RootModel[dict[str, S3SitelinkData]]):
    """Hash map for entity sitelinks by site, including title hash and badges."""
