#!/usr/bin/env python3
"""Generate overview documentation for database schema from live database."""

import sys
from pathlib import Path
from typing import Dict, List


def extract_schema_from_database() -> List[Dict[str, str]]:
    """Extract schema information from Vitess database."""
    try:
        import pymysql
        sys.path.insert(0, "src")
        from models.config.settings import settings
    except ImportError as e:
        print(f"Error: Required dependencies not available: {e}")
        print("Install with: pip install pymysql")
        return []

    # Extract table creation statements from repository files
    tables = []

    # Find all CREATE TABLE statements in repository files
    repos_dir = Path("src/models/infrastructure/vitess/repositories")
    if repos_dir.exists():
        for repo_file in repos_dir.glob("*.py"):
            if repo_file.name == "__init__.py":
                continue

            try:
                with open(repo_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Find CREATE TABLE statements
                table_info = extract_create_table_from_content(content, str(repo_file.relative_to(Path("src"))))
                if table_info:
                    tables.append(table_info)
            except Exception as e:
                print(f"Warning: Could not parse {repo_file}: {e}", file=sys.stderr)

    return tables


def extract_create_table_from_content(content: str, file_location: str) -> Dict[str, str]:
    """Extract CREATE TABLE statement from file content."""
    import re

    # Look for cursor.execute("""\nCREATE TABLE...""")
    sql_blocks = re.findall(
        r'cursor\.execute\(\s*"""\s*(CREATE TABLE[^"]+?)\s*"""\)',
        content,
        re.DOTALL | re.IGNORECASE,
    )

    if not sql_blocks:
        return {}

    sql = sql_blocks[0].strip()

    # Extract table name
    table_match = re.search(r'CREATE TABLE\s+[`"]?(\w+)[`"]?\s*\(', sql, re.IGNORECASE)
    if not table_match:
        return {}

    table_name = table_match.group(1)

    # Clean up SQL
    cleaned_sql = re.sub(r"\s+", " ", sql)

    # Extract column definitions
    columns = []
    paren_match = re.search(r"\((.*?)\)", sql, re.DOTALL)
    if paren_match:
        column_defs = paren_match.group(1)
        lines = [line.strip() for line in column_defs.split(",") if line.strip()]

        for line in lines:
            if any(keyword in line.upper() for keyword in ["PRIMARY KEY", "FOREIGN KEY", "INDEX", "UNIQUE"]):
                continue

            col_match = re.match(r'[`"]?(\w+)[`"]?\s+([^,\n\(]+)', line)
            if col_match:
                col_name, col_type = col_match.groups()
                columns.append(f"- `{col_name}`: {col_type.strip()}")

    return {
        "name": table_name,
        "location": file_location,
        "sql": cleaned_sql,
        "columns": columns,
    }


def generate_entity_relationship_diagram(tables: List[Dict[str, str]]) -> str:
    """Generate a simple ER diagram in Mermaid format."""
    import re
    lines = ["## Entity Relationship Diagram\n", "```mermaid", "erDiagram"]

    relationships = []

    for table in tables:
        sql = table["sql"].lower()

        # Look for foreign key references
        fk_matches = re.findall(
            r"foreign key\s*\(\s*(\w+)\s*\)\s*references\s*[`\"]?(\w+)[`\"]?\s*\(\s*(\w+)\s*\)",
            sql,
        )

        for fk_match in fk_matches:
            from_col, to_table, to_col = fk_match
            relationships.append(f"    {table['name']} ||--o{{ {to_table} : {from_col} }}")

    # Add all tables
    for table in tables:
        lines.append(f"    {table['name']} {{")
        for col in table["columns"][:7]:
            lines.append(f"        {col}")
        if len(table["columns"]) > 7:
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
    # Group tables by type
    entity_tables = [t for t in tables if any(
        keyword in t["name"].lower()
        for keyword in ["entity", "revision", "head", "redirect", "backlink", "statement", "snak", "reference", "qualifier"]
    )]

    user_tables = [t for t in tables if "user" in t["name"].lower()]

    stats_tables = [t for t in tables if any(
        keyword in t["name"].lower()
        for keyword in ["stats", "statistics"]
    )]

    other_tables = [t for t in tables if t not in entity_tables and t not in user_tables and t not in stats_tables]

    lines = [
        "# Database Schema Overview\n",
        "This document describes Vitess database schema used by wikibase-backend.\n",
        "## Summary\n",
        f"- **Total Tables**: {len(tables)}",
        "- **Database**: MySQL (via Vitess)",
        "- **Schema Location**: Distributed across repository files in `src/models/infrastructure/vitess/repositories/`\n",
    ]

    # Entity Tables
    if entity_tables:
        lines.append("## Entity Tables\n")
        for table in entity_tables:
            lines.append(f"### {table['name']}\n")
            lines.append(f"**Location**: `src/{table['location']}`\n")

            if table["columns"]:
                lines.append("**Columns**:\n")
                for col in table["columns"]:
                    lines.append(col)
                lines.append("")

            lines.append("**SQL Definition**:\n")
            lines.append(f"```sql\n{table['sql']}\n```\n")

    # User Tables
    if user_tables:
        lines.append("## User Tables\n")
        for table in user_tables:
            lines.append(f"### {table['name']}\n")
            lines.append(f"**Location**: `src/{table['location']}`\n")

            if table["columns"]:
                lines.append("**Columns**:\n")
                for col in table["columns"]:
                    lines.append(col)
                lines.append("")

            lines.append("**SQL Definition**:\n")
            lines.append(f"```sql\n{table['sql']}\n```\n")

    # Statistics Tables
    if stats_tables:
        lines.append("## Statistics Tables\n")
        for table in stats_tables:
            lines.append(f"### {table['name']}\n")
            lines.append(f"**Location**: `src/{table['location']}`\n")

            if table["columns"]:
                lines.append("**Columns**:\n")
                for col in table["columns"]:
                    lines.append(col)
                lines.append("")

            lines.append("**SQL Definition**:\n")
            lines.append(f"```sql\n{table['sql']}\n```\n")

    # Other Tables
    if other_tables:
        lines.append("## Other Tables\n")
        for table in other_tables:
            lines.append(f"### {table['name']}\n")
            lines.append(f"**Location**: `src/{table['location']}`\n")

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
    lines.append("- All tables use appropriate data types for their content")
    lines.append("- Foreign key relationships are enforced at the application level")
    lines.append("- Indexes are optimized for most common query patterns")
    lines.append("- Schema is applied automatically during Vitess initialization via repository files")
    lines.append("- BIGINT types are used for Vitess compatibility and scalability")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    print("Extracting database schema from repository files...")

    tables = extract_schema_from_database()

    if not tables:
        print("No tables found")
        return

    print(f"Found {len(tables)} tables")

    # Generate markdown
    markdown = generate_markdown(tables)

    # Output to stdout (will be redirected by update-docs.sh)
    print(markdown)


if __name__ == "__main__":
    main()
