import json

from rapidhash import rapidhash

from models.internal_representation.statements import Statement


class StatementHasher:
    @staticmethod
    def compute_hash(statement: Statement) -> int:
        """Compute rapidhash of full statement JSON (mainsnak + qualifiers + references)

        Hash includes:
        - property (property ID)
        - value (main statement value)
        - rank (preferred/normal/deprecated)
        - qualifiers (additional context)
        - references (sources)

        Hash excludes:
        - statement_id (GUID, not content)

        Args:
            statement: Statement object to hash

        Returns:
            64-bit rapidhash integer
        """
        statement_dict = statement.model_dump(exclude={"statement_id"})
        canonical_json = json.dumps(statement_dict, sort_keys=True)
        return rapidhash(canonical_json.encode())
