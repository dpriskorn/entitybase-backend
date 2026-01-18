"""Utilities for computing reference hashes."""

import json
from typing import Any, Union
from rapidhash import rapidhash


class ReferenceHasher:
    """Utilities for computing reference content hashes."""

    @staticmethod
    def compute_hash(reference: Union[dict[str, Any], "Reference"]) -> int:  # type: ignore[name-defined]
        """Compute rapidhash of full reference JSON.

        Hash includes:
        - snaks (property-value pairs)
        - snaks-order

        Hash excludes:
        - hash (existing hash field, not content)

        Args:
            reference: Reference dict or Reference object to hash.

        Returns:
            64-bit rapidhash integer.
        """
        if isinstance(reference, dict):
            reference_dict = reference
        else:
            reference_dict = reference.model_dump()
        reference_for_hash = {k: v for k, v in reference_dict.items() if k != "hash"}
        canonical_json = json.dumps(reference_for_hash, sort_keys=True)
        return rapidhash(canonical_json.encode())  # type: ignore[no-any-return]
