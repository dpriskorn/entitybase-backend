#!/usr/bin/env python3
"""Generate overview documentation for application configuration."""

import ast
from pathlib import Path
from typing import Dict, List, Tuple


def parse_settings_file() -> Dict[str, List[Dict[str, str]]]:
    """Parse the settings file to extract configuration options."""
    settings_file = Path("src/models/config/settings.py")

    if not settings_file.exists():
        print("Error: Settings file not found")
        return {}

    with open(settings_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse the Settings class
    tree = ast.parse(content)

    settings = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Settings":
            # Find all assignments in the class
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    setting_name = (
                        item.target.id
                        if isinstance(item.target, ast.Name)
                        else str(item.target)
                    )

                    # Skip if it's not a field (like model_config)
                    if setting_name == "model_config":
                        continue

                    # Get the default value
                    default_value = "Not specified"
                    if item.value:
                        default_value = ast.unparse(item.value)

                    # Get type annotation
                    field_type = "Any"
                    if item.annotation:
                        field_type = ast.unparse(item.annotation)

                    # Look for comments above the field
                    description = extract_field_description(content, item.lineno)

                    settings[setting_name] = {
                        "type": field_type,
                        "default": default_value,
                        "description": description,
                    }

    return {"Settings": list(settings.items())}


def extract_field_description(content: str, lineno: int) -> str:
    """Extract description from comments above a field."""
    lines = content.split("\n")
    # Look backwards from the field line for comments
    for i in range(lineno - 2, max(lineno - 10, 0), -1):
        line = lines[i].strip()
        if line.startswith("#"):
            return line[1:].strip()
        elif line and not line.startswith(" ") and not line.startswith("\t"):
            # Hit another field or class definition
            break

    return "No description available"


def categorize_settings(
    settings_items: List[Tuple[str, Dict[str, str]]],
) -> Dict[str, List[Tuple[str, Dict[str, str]]]]:
    """Categorize settings by functionality."""
    categories = {
        "Database": [],
        "Storage": [],
        "API": [],
        "Workers": [],
        "RDF": [],
        "Development": [],
        "Other": [],
    }

    for setting_name, setting_info in settings_items:
        name_lower = setting_name.lower()

        if any(keyword in name_lower for keyword in ["vitess", "mysql", "database"]):
            categories["Database"].append((setting_name, setting_info))
        elif any(keyword in name_lower for keyword in ["s3", "minio", "bucket"]):
            categories["Storage"].append((setting_name, setting_info))
        elif any(
            keyword in name_lower for keyword in ["api", "endpoint", "port", "host"]
        ):
            categories["API"].append((setting_name, setting_info))
        elif any(keyword in name_lower for keyword in ["worker", "backlink"]):
            categories["Workers"].append((setting_name, setting_info))
        elif any(keyword in name_lower for keyword in ["rdf", "turtle", "sparql"]):
            categories["RDF"].append((setting_name, setting_info))
        elif any(keyword in name_lower for keyword in ["log", "test", "debug"]):
            categories["Development"].append((setting_name, setting_info))
        else:
            categories["Other"].append((setting_name, setting_info))

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def generate_markdown(
    categorized_settings: Dict[str, List[Tuple[str, Dict[str, str]]]],
) -> str:
    """Generate markdown overview of configuration."""
    lines = ["# Configuration Overview\n"]

    lines.append(
        "This document describes all configuration options available in wikibase-backend.\n"
    )
    lines.append(
        "Settings are managed through the `Settings` class in `src/models/config/settings.py`.\n"
    )

    # Environment Variables section
    lines.append("## Environment Variables\n")
    lines.append(
        "All settings can be overridden using environment variables with the same name.\n\n"
    )

    # Settings by category
    for category, settings_list in categorized_settings.items():
        lines.append(f"## {category} Settings\n")

        for setting_name, setting_info in settings_list:
            lines.append(f"### `{setting_name}`\n")
            lines.append(f"- **Type**: `{setting_info['type']}`")
            lines.append(f"- **Default**: `{setting_info['default']}`")
            lines.append(f"- **Description**: {setting_info['description']}\n")

    # Usage example
    lines.append("## Usage Example\n")
    lines.append(
        "```python\nfrom models.config.settings import settings\n\n# Access a setting\napi_port = settings.api_port\n\n# Override via environment\n# export VITESS_HOST=my-custom-host\n```\n"
    )

    # Docker section
    lines.append("## Docker Configuration\n")
    lines.append("Key settings for Docker deployment:\n\n")
    lines.append("- `VITESS_HOST`: Vitess database host (default: vitess)")
    lines.append("- `VITESS_PORT`: Vitess database port (default: 15309)")
    lines.append(
        "- `S3_ENDPOINT`: S3-compatible storage endpoint (default: http://minio:9000)"
    )
    lines.append("- `KAFKA_BROKERS`: Kafka broker addresses for change streaming")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    settings_data = parse_settings_file()

    if not settings_data:
        print("No settings found")
        return

    # Get settings list
    settings_list = settings_data.get("Settings", [])

    # Categorize settings
    categorized = categorize_settings(settings_list)

    # Generate markdown
    markdown = generate_markdown(categorized)

    # Output to stdout (will be redirected by update-docs.sh)
    print(markdown)


if __name__ == "__main__":
    main()
