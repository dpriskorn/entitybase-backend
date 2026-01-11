#!/usr/bin/env python3
"""Generate overview documentation for database schema."""

import re
from pathlib import Path
from typing import Dict, List, Tuple


def parse_schema_file() -> List[Dict[str, str]]:
    """Parse the Vitess schema file to extract table definitions."""
    schema_file = Path("src/models/infrastructure/vitess/schema.py")

    if not schema_file.exists():
        print("Error: Schema file not found")
        return []

    with open(schema_file, "r", encoding="utf-8") as f:
        content = f.read()

    tables = []

    # Find CREATE TABLE statements between triple quotes
    # Look for the pattern: cursor.execute("""\nCREATE TABLE...
    sql_blocks = re.findall(
        r'cursor\.execute\(\s*"""\s*(CREATE TABLE.*?)\s*"""\s*\)',
        content,
        re.DOTALL | re.IGNORECASE,
    )

    for sql in sql_blocks:
        table_info = parse_create_table_statement(sql.strip())
        if table_info:
            tables.append(table_info)

    return tables


def parse_create_table_statement(sql: str) -> Dict[str, str]:
    """Parse a CREATE TABLE statement to extract table information."""
    # Extract table name
    table_match = re.search(r"CREATE TABLE.*?(\w+)\s*\(", sql, re.IGNORECASE)
    if not table_match:
        return {}

    table_name = table_match.group(1)

    # Clean up the SQL for display
    cleaned_sql = re.sub(r"\s+", " ", sql.strip())
    cleaned_sql = re.sub(r",\s*,", ",", cleaned_sql)  # Remove double commas

    # Extract column definitions
    columns = []
    # Find content between parentheses
    paren_match = re.search(r"\((.*?)\)", sql, re.DOTALL)
    if paren_match:
        column_defs = paren_match.group(1)
        # Split by commas, but be careful with commas inside functions
        lines = [line.strip() for line in column_defs.split(",") if line.strip()]

        for line in lines:
            if "PRIMARY KEY" in line or "FOREIGN KEY" in line or "INDEX" in line:
                continue  # Skip constraints for now
            # Extract column name and type
            col_match = re.match(r"(\w+)\s+([^,\n]+)", line)
            if col_match:
                col_name, col_type = col_match.groups()
                columns.append(f"- `{col_name}`: {col_type.strip()}")

    return {
        "name": table_name,
        "sql": cleaned_sql,
        "columns": columns,
    }


def generate_entity_relationship_diagram(tables: List[Dict[str, str]]) -> str:
    """Generate a simple ER diagram in ASCII/Markdown format."""
    lines = ["## Entity Relationship Diagram\n", "```mermaid", "erDiagram"]

    # Map table relationships based on foreign keys
    relationships = []

    for table in tables:
        sql = table["sql"].lower()

        # Look for foreign key references
        fk_matches = re.findall(
            r"foreign key\s*\(\s*(\w+)\s*\)\s*references\s*(\w+)\s*\(\s*(\w+)\s*\)", sql
        )

        for fk_match in fk_matches:
            from_col, to_table, to_col = fk_match
            relationships.append(
                f"    {table['name']} ||--o{{ {to_table} : {from_col} }}"
            )

    # Add all tables
    for table in tables:
        lines.append(f"    {table['name']} {{")
        for col in table["columns"][:5]:  # Show first 5 columns
            lines.append(f"        {col}")
        if len(table["columns"]) > 5:
            lines.append(f"        ... ({len(table['columns'])} total columns)")
        lines.append("    }")

    # Add relationships
    if relationships:
        lines.append("")
        lines.extend(relationships)

    lines.append("```")

    return "\n".join(lines)


def generate_markdown(tables: List[Dict[str, str]]) -> str:
    """Generate markdown overview of database schema."""
    lines = ["# Database Schema Overview\n"]

    lines.append(
        "This document describes the Vitess database schema used by wikibase-backend.\n"
    )

    # Summary
    lines.append(f"## Summary\n")
    lines.append(f"- **Total Tables**: {len(tables)}")
    lines.append("- **Database**: MySQL (via Vitess)")
    lines.append("- **Schema File**: `src/models/infrastructure/vitess/schema.py`\n")

    # Tables
    lines.append("## Tables\n")

    for table in tables:
        lines.append(f"### {table['name']}\n")

        if table["columns"]:
            lines.append("**Columns**:\n")
            for col in table["columns"]:
                lines.append(col)
            lines.append("")

        lines.append("**SQL Definition**:\n")
        lines.append(f"```sql\n{table['sql']}\n```\n")

    # ER Diagram
    er_diagram = generate_entity_relationship_diagram(tables)
    lines.append(er_diagram)

    # Additional Notes
    lines.append("\n## Notes\n")
    lines.append("- All tables use BIGINT primary keys for Vitess compatibility")
    lines.append("- Foreign key relationships are enforced at the application level")
    lines.append("- Indexes are optimized for the most common query patterns")
    lines.append("- Schema is applied automatically during Vitess initialization")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    tables = parse_schema_file()

    if not tables:
        print("No tables found in schema file")
        return

    # Generate markdown
    markdown = generate_markdown(tables)

    # Output to stdout (will be redirected by update-docs.sh)
    print(markdown)


if __name__ == "__main__":
    main()
