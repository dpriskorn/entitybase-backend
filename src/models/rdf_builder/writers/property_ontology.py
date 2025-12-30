from typing import TextIO


class PropertyOntologyWriter:
    @staticmethod
    def write_property(output: TextIO, property_id: str):
        """Write property ontology with all predicate declarations"""
        output.write(f'wd:{property_id} a wikibase:Property .\n')
        output.write(f'p:{property_id} a owl:ObjectProperty .\n')
        output.write(f'psv:{property_id} a owl:ObjectProperty .\n')
        output.write(f'pqv:{property_id} a owl:ObjectProperty .\n')
        output.write(f'prv:{property_id} a owl:ObjectProperty .\n')
        output.write(f'wdt:{property_id} a owl:ObjectProperty .\n')
        output.write(f'ps:{property_id} a owl:ObjectProperty .\n')
        output.write(f'pq:{property_id} a owl:ObjectProperty .\n')
        output.write(f'pr:{property_id} a owl:ObjectProperty .\n')
