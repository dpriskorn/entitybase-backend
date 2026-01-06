# src/models/rdf_builder/writers/property.py

from typing import TextIO

from models.internal_representation.property_metadata import PropertyMetadata


class PropertyWriter:
    @staticmethod
    def write_property(output: TextIO, prop: PropertyMetadata) -> None:
        pid = prop.property_id
        wd = f"wd:{pid}"

        output.write(f"{wd} a wikibase:Property .\n")
        output.write(
            f"{wd} wikibase:propertyType wikibase:{PropertyWriter._property_type(prop)} .\n"
        )

        output.write(f"{wd} wikibase:claim p:{pid} .\n")
        output.write(f"{wd} wikibase:statementProperty ps:{pid} .\n")
        output.write(f"{wd} wikibase:qualifier pq:{pid} .\n")
        output.write(f"{wd} wikibase:directClaim wdt:{pid} .\n")
        output.write(f"{wd} wikibase:reference pr:{pid} .\n")

    @staticmethod
    def _property_type(prop: PropertyMetadata) -> str:
        return {
            "wikibase-item": "WikibaseItem",
            "string": "String",
            "time": "Time",
            "quantity": "Quantity",
            "globe-coordinate": "GlobeCoordinate",
            "monolingualtext": "Monolingualtext",
            "commonsMedia": "CommonsMedia",
            "external-id": "ExternalId",
            "url": "Url",
        }[prop.datatype.value]
