"""Utilities for computing statement hashes."""

import json
from typing import Any, Union
from rapidhash import rapidhash


class StatementHasher:
    """Utilities for computing statement content hashes."""

    @staticmethod
    def compute_hash(statement: Union[dict[str, Any], "Statement"]) -> int:  # type: ignore[name-defined]
        """Compute rapidhash of full statement JSON (mainsnak + qualifiers + references).

        Hash includes:
        - property (property ID)
        - value (main statement value)
        - rank (preferred/normal/deprecated)
        - qualifiers (additional context)
        - references (sources)

        Hash excludes:
        - id (GUID, not content)

        Args:
            statement: Statement dict or Statement object to hash.

        Returns:
            64-bit rapidhash integer.
        """
        from models.internal_representation.statements import Statement

        if isinstance(statement, Statement):
            statement_dict = statement.model_dump()
        else:
            statement_dict = statement
        statement_for_hash = {
            k: v for k, v in statement_dict.items() if k != "statement_id"
        }
        canonical_json = json.dumps(statement_for_hash, sort_keys=True)
        return rapidhash(canonical_json.encode())  # type: ignore[no-any-return]
