"""Utilities for computing qualifier hashes."""

import json
from typing import Any, Union
from rapidhash import rapidhash


class QualifierHasher:
    """Utilities for computing qualifier content hashes."""

    @staticmethod
    def compute_hash(qualifiers: Union[dict[str, Any], "Qualifiers"]) -> int:  # type: ignore[name-defined]
        """Compute rapidhash of full qualifiers JSON.

        Hash includes the entire qualifiers object (property map to snak arrays).

        Args:
            qualifiers: Qualifiers dict or Qualifiers object to hash.

        Returns:
            64-bit rapidhash integer.
        """
        if isinstance(qualifiers, dict):
            qualifiers_dict = qualifiers
        else:
            qualifiers_dict = qualifiers.model_dump()
        canonical_json = json.dumps(qualifiers_dict, sort_keys=True)
        return rapidhash(canonical_json.encode())  # type: ignore[no-any-return]
