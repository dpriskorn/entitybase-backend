"""Sitelinks hashes model."""

from pydantic.root_model import RootModel


class SitelinksHashes(RootModel[dict[str, int]]):
    """Hash map for entity sitelinks by site."""