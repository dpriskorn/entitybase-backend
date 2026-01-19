import pytest

pytestmark = pytest.mark.unit

from models.internal_representation.vocab import Vocab


class TestVocab:
    def test_vocab_constants(self) -> None:
        vocab = Vocab()
        assert vocab.WD == "http://www.wikidata.org/entity/"
        assert vocab.WDT == "http://www.wikidata.org/prop/direct/"
        assert vocab.P == "http://www.wikidata.org/prop/"
        assert vocab.PS == "http://www.wikidata.org/prop/statement/"
        assert vocab.PQ == "http://www.wikidata.org/prop/qualifier/"
        assert vocab.PR == "http://www.wikidata.org/prop/reference/"
        assert vocab.WDS == "http://www.wikidata.org/entity/statement/"
        assert vocab.WDREF == "http://www.wikidata.org/reference/"
