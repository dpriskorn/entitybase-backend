from pydantic import BaseModel


class URIGenerator:
    """This is intentionally not a BaseModel class"""
    WD: str = "http://www.wikidata.org/entity"
    DATA: str = "http://www.wikidata.org/wiki/Special:EntityData"
    WDS: str = "http://www.wikidata.org/entity/statement"

    @staticmethod
    def entity_uri(entity_id: str) -> str:
        return f"{URIGenerator.WD}/{entity_id}"

    @staticmethod
    def data_uri(entity_id: str) -> str:
        return f"{URIGenerator.DATA}/{entity_id}.ttl"

    @staticmethod
    def statement_uri(statement_id: str) -> str:
        return f"{URIGenerator.WDS}/{statement_id}"

    @staticmethod
    def reference_uri(statement_uri: str, ref_index: int) -> str:
        return f"{statement_uri}-{ref_index:09d}#ref"
