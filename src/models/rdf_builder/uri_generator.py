class URIGenerator:
    """Generate URIs for entities, statements, references"""

    BASE_URI = "http://acme.test"  # From test data
    DATA_URI = "http://data.acme.test"

    @staticmethod
    def entity_uri(entity_id: str) -> str:
        return f"{URIGenerator.BASE_URI}/{entity_id}"

    @staticmethod
    def data_uri(entity_id: str) -> str:
        return f"{URIGenerator.DATA_URI}/{entity_id}"

    @staticmethod
    def statement_uri(statement_id: str) -> str:
        return f"{URIGenerator.BASE_URI}/statement/{statement_id}"

    @staticmethod
    def reference_uri(statement_uri: str, ref_index: int) -> str:
        return f"{statement_uri}-{ref_index:09d}#ref"
