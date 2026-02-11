"""Unit tests for tabular_data_value_parser."""

import pytest

from models.json_parser.values.tabular_data_value_parser import parse_tabular_data_value
from models.internal_representation.values.tabular_data_value import TabularDataValue


class TestTabularDataValueParser:
    """Unit tests for tabular data value parser."""

    def test_parse_valid_tabular_data_value(self):
        """Test parsing a valid tabular data value."""
        datavalue = {"value": "Data:Population_statistics.csv"}

        result = parse_tabular_data_value(datavalue)

        assert isinstance(result, TabularDataValue)
        assert result.kind == "tabular_data"
        assert result.value == "Data:Population_statistics.csv"
        assert result.datatype_uri == "http://wikiba.se/ontology#TabularData"

    def test_parse_tabular_data_value_csv_file(self):
        """Test parsing a tabular data value with CSV file."""
        datavalue = {"value": "Data:survey_results.csv"}

        result = parse_tabular_data_value(datavalue)

        assert result.value == "Data:survey_results.csv"

    def test_parse_tabular_data_value_excel_file(self):
        """Test parsing a tabular data value with Excel file."""
        datavalue = {"value": "Data:financial_data.xlsx"}

        result = parse_tabular_data_value(datavalue)

        assert result.value == "Data:financial_data.xlsx"

    def test_parse_tabular_data_value_tsv_file(self):
        """Test parsing a tabular data value with TSV file."""
        datavalue = {"value": "Data:gene_data.tsv"}

        result = parse_tabular_data_value(datavalue)

        assert result.value == "Data:gene_data.tsv"

    def test_parse_tabular_data_value_empty_string(self):
        """Test parsing an empty tabular data value."""
        datavalue = {"value": ""}

        result = parse_tabular_data_value(datavalue)

        assert result.value == ""

    def test_parse_tabular_data_value_missing_value(self):
        """Test parsing when the value field is missing."""
        datavalue = {}

        result = parse_tabular_data_value(datavalue)

        assert isinstance(result, TabularDataValue)
        assert result.value == ""  # Empty string default

    def test_parse_tabular_data_value_different_formats(self):
        """Test parsing tabular data values in different formats."""
        formats = [
            "Data:data.json",
            "Data:table.xml",
            "Data:spreadsheet.ods",
            "Data:database.sqlite",
        ]

        for fmt in formats:
            datavalue = {"value": fmt}
            result = parse_tabular_data_value(datavalue)
            assert result.value == fmt

    def test_parse_tabular_data_value_unicode_filename(self):
        """Test parsing a tabular data value with unicode characters."""
        datavalue = {"value": "Data:данные_таблицы.csv"}

        result = parse_tabular_data_value(datavalue)

        assert result.value == "Data:данные_таблицы.csv"

    def test_parse_tabular_data_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": "Data:sample_data.csv"}

        result = parse_tabular_data_value(datavalue)

        assert isinstance(result, TabularDataValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_tabular_data_value_long_filename(self):
        """Test parsing a tabular data value with a very long filename."""
        long_filename = "Data:" + "A" * 200 + ".csv"
        datavalue = {"value": long_filename}

        result = parse_tabular_data_value(datavalue)

        assert result.value == long_filename
