from typing import TextIO

from models.rdf_builder.uri_generator import URIGenerator


class ValueNodeWriter:
    """Write structured value nodes (wdv:) for time, quantity, globe-coordinate"""

    uri = URIGenerator()

    @staticmethod
    def write_time_value_node(output: TextIO, value_id: str, time_value):
        """Write time value node block"""
        time_str = time_value.value.lstrip('+')
        output.write(f'wdv:{value_id} a wikibase:TimeValue ;\n')
        output.write(f'\twikibase:timeValue "{time_str}"^^xsd:dateTime ;\n')
        output.write(f'\twikibase:timePrecision "{time_value.precision}"^^xsd:integer ;\n')
        output.write(f'\twikibase:timeTimezone "{time_value.timezone}"^^xsd:integer ;\n')
        output.write(f'\twikibase:timeCalendarModel <{time_value.calendarmodel}> .\n')

    @staticmethod
    def write_quantity_value_node(output: TextIO, value_id: str, quantity_value):
        """Write quantity value node block"""
        output.write(f'wdv:{value_id} a wikibase:QuantityValue ;\n')
        output.write(f'\twikibase:quantityAmount "{quantity_value.value}"^^xsd:decimal ;\n')
        output.write(f'\twikibase:quantityUnit <{quantity_value.unit}>')

        if quantity_value.upper_bound:
            output.write(f' ;\n')
            output.write(f'\twikibase:quantityUpperBound "{quantity_value.upper_bound}"^^xsd:decimal')

        if quantity_value.lower_bound:
            if not quantity_value.upper_bound:
                output.write(f' ;\n')
            output.write(f'\twikibase:quantityLowerBound "{quantity_value.lower_bound}"^^xsd:decimal')

        output.write(f' .\n')

    @staticmethod
    def write_globe_value_node(output: TextIO, value_id: str, globe_value):
        """Write globe coordinate value node block"""
        precision_formatted = f"{globe_value.precision:.1E}".replace("E-0", "E-").replace("E+0", "E+")
        output.write(f'wdv:{value_id} a wikibase:GlobecoordinateValue ;\n')
        output.write(f'\twikibase:geoLatitude "{globe_value.latitude}"^^xsd:double ;\n')
        output.write(f'\twikibase:geoLongitude "{globe_value.longitude}"^^xsd:double ;\n')
        output.write(f'\twikibase:geoPrecision "{precision_formatted}"^^xsd:double ;\n')
        output.write(f'\twikibase:geoGlobe <{globe_value.globe}> .\n')
