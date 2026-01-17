"""Vocabulary constants for Wikibase."""

from pydantic import BaseModel


class Vocab(BaseModel):
    """Wikibase vocabulary prefixes."""

    WD: str = "http://www.wikidata.org/entity/"
    WDT: str = "http://www.wikidata.org/prop/direct/"
    P: str = "http://www.wikidata.org/prop/"
    PS: str = "http://www.wikidata.org/prop/statement/"
    PQ: str = "http://www.wikidata.org/prop/qualifier/"
    PR: str = "http://www.wikidata.org/prop/reference/"
    WDS: str = "http://www.wikidata.org/entity/statement/"
    WDREF: str = "http://www.wikidata.org/reference/"
