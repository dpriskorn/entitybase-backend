import json
from typing import Any

from rapidhash import rapidhash


class StatementHasher:
    @staticmethod
    def compute_hash(statement_dict: dict[str, Any]) -> int:
        """Compute rapidhash of full statement JSON (mainsnak + qualifiers + references)

        Hash includes:
        - property (property ID)
        - value (main statement value)
        - rank (preferred/normal/deprecated)
        - qualifiers (additional context)
        - references (sources)

        Hash excludes:
        - id (GUID, not content)

        Args:
            statement_dict: Statement dict to hash

        Returns:
            64-bit rapidhash integer
        """
        statement_for_hash = {k: v for k, v in statement_dict.items() if k != "id"}
        canonical_json = json.dumps(statement_for_hash, sort_keys=True)
        return rapidhash(canonical_json.encode())
