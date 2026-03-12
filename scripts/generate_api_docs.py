#!/usr/bin/env python3
"""Generate API documentation from FastAPI app."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.rest_api.main import app


def get_openapi_spec() -> dict:
    """Get the OpenAPI specification from the app."""
    return app.openapi()


def get_schema_example(schema: dict) -> str | None:
    """Generate example JSON from a schema."""
    if schema.get("type") == "object" and "properties" in schema:
        example = {}
        for prop_name, prop_schema in schema["properties"].items():
            example[prop_name] = get_field_example(prop_schema)
        return json.dumps(example, indent=2)
    elif schema.get("type") == "array" and "items" in schema:
        item = get_field_example(schema["items"])
        return json.dumps([item], indent=2)
    return None


def get_field_example(field_schema: dict) -> str | dict | list | int | float | bool | None:
    """Generate example for a single field."""
    if "example" in field_schema:
        return field_schema["example"]

    field_type = field_schema.get("type")

    if field_type == "string":
        if "enum" in field_schema:
            return field_schema["enum"][0]
        return "string"
    elif field_type == "integer":
        return 0
    elif field_type == "number":
        return 0.0
    elif field_type == "boolean":
        return True
    elif field_type == "array":
        return [get_field_example(field_schema.get("items", {}))]
    elif field_type == "object":
        if "properties" in field_schema:
            return {k: get_field_example(v) for k, v in field_schema["properties"].items()}
        return {}
    return None


def extract_ref_name(ref: str) -> str:
    """Extract component name from $ref."""
    if ref and ref.startswith("#/components/schemas/"):
        return ref.split("/")[-1]
    return ref


def get_schema_details(schema_name: str, openapi_spec: dict) -> dict | None:
    """Get full schema details from components."""
    schemas = openapi_spec.get("components", {}).get("schemas", {})
    return schemas.get(schema_name)


def generate_markdown(openapi_spec: dict) -> str:
    """Generate markdown documentation from OpenAPI spec."""
    md = []
    md.append("# Entitybase Backend API Documentation\n")
    md.append(f"**Version**: {openapi_spec.get('info', {}).get('version', 'N/A')}\n")
    md.append(f"**Base URL**: See `/docs` for interactive API explorer\n")
    md.append("\n---\n\n")

    info = openapi_spec.get("info", {})
    if info.get("description"):
        md.append(f"{info['description']}\n\n")

    md.append("## Quick Start: Creating Entities\n\n")
    md.append("### Creating an Item\n\n")
    md.append("**Note:** Currently, item creation only supports empty items. Use the endpoint below to create an item, then add labels/descriptions using the update endpoints.\n\n")
    md.append("```bash\n")
    md.append("# Create an empty item\n")
    md.append("curl -X POST https://api.example.com/v1/entitybase/entities/items \\\n")
    md.append("  -H \"X-User-ID: 1\" \\\n")
    md.append("  -H \"X-Edit-Summary: Creating new item\"\n")
    md.append("```\n\n")
    md.append("### Creating a Lexeme (with full data)\n\n")
    md.append("Lexeme creation supports full entity data in the request body:\n\n")
    md.append("```json\n")
    md.append("{\n")
    md.append('  "type": "lexeme",\n')
    md.append('  "language": "Q1860",\n')
    md.append('  "lexicalCategory": "Q1084",\n')
    md.append('  "lemmas": {"en": {"language": "en", "value": "test"}},\n')
    md.append('  "labels": {"en": {"language": "en", "value": "test lexeme"}},\n')
    md.append('  "forms": [\n')
    md.append('    {\n')
    md.append('      "representations": {"en": {"language": "en", "value": "tests"}},\n')
    md.append('      "grammaticalFeatures": ["Q110786"]\n')
    md.append('    }\n')
    md.append('  ],\n')
    md.append('  "senses": [\n')
    md.append('    {\n')
    md.append('      "glosses": {"en": {"language": "en", "value": "a test"}}\n')
    md.append('    }\n')
    md.append('  ]\n')
    md.append("}\n")
    md.append("```\n\n")
    md.append("### Adding Labels and Descriptions to Existing Entities\n\n")
    md.append("After creating an entity, add labels using:\n\n")
    md.append("```bash\n")
    md.append("# Add a label\n")
    md.append("curl -X PUT https://api.example.com/v1/entitybase/entities/Q123/labels/en \\\n")
    md.append("  -H \"Content-Type: application/json\" \\\n")
    md.append("  -H \"X-User-ID: 1\" \\\n")
    md.append("  -H \"X-Edit-Summary: Adding label\" \\\n")
    md.append("  -d '{\"language\": \"en\", \"value\": \"My Item\"}'\n")
    md.append("```\n\n")
    md.append("### MonolingualText Format\n\n")
    md.append("Labels, descriptions, aliases, and other term data use the MonolingualText format:\n\n")
    md.append("```json\n")
    md.append("{\n")
    md.append('  "language": "en",\n')
    md.append('  "value": "The text content"\n')
    md.append("}\n")
    md.append("```\n\n")
    md.append("---\n\n")

    servers = openapi_spec.get("servers", [])
    if servers:
        md.append("## Base URL\n")
        for server in servers:
            md.append(f"- {server.get('url', '')}")
        md.append("\n")

    md.append("## Authentication\n")
    md.append("All endpoints requiring modifications (POST, PUT, PATCH, DELETE) require headers:\n")
    md.append("| Header | Type | Required | Description |\n")
    md.append("|--------|------|----------|-------------|\n")
    md.append("| `X-User-ID` | integer | Yes | User ID making the edit |\n")
    md.append("| `X-Edit-Summary` | string | Yes | Edit summary (1-200 chars) |\n")
    md.append("| `X-Base-Revision-ID` | integer | No | For optimistic locking |\n")
    md.append("\n---\n\n")

    tags = openapi_spec.get("tags", [])
    paths = openapi_spec.get("paths", {})
    schemas = openapi_spec.get("components", {}).get("schemas", {})

    # Collect unique tags from all endpoints
    endpoint_tags = set()
    for path, methods in paths.items():
        for method, details in methods.items():
            for tag in details.get("tags", []):
                endpoint_tags.add(tag)

    tag_order = ["items", "properties", "lexemes", "entities", "statements", "statistics", "watchlist", "import", "redirects", "list", "debug", "health", "version", "settings"]

    def sort_key(tag_name: str) -> int:
        try:
            return tag_order.index(tag_name)
        except ValueError:
            return len(tag_order)

    sorted_tags = sorted(endpoint_tags, key=sort_key)

    for tag_name in sorted_tags:
        md.append(f"## {tag_name.title()}\n")

        tag_endpoints = []
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                    if tag_name in details.get("tags", []):
                        tag_endpoints.append((path, method.upper(), details))

        tag_endpoints.sort(key=lambda x: (x[0], x[1]))

        for path, method, details in tag_endpoints:
            md.append(f"### {method} {path}\n")

            summary = details.get("summary", "")
            description = details.get("description", "")

            if summary:
                md.append(f"**{summary}**\n")
            if description:
                md.append(f"{description}\n")

            md.append("| Aspect | Details |\n")
            md.append("|--------|---------|\n")

            operation_id = details.get("operationId", "")
            if operation_id:
                md.append(f"| Operation ID | `{operation_id}` |\n")

            md.append(f"| Method | `{method}` |\n")
            md.append(f"| Path | `{path}` |\n")

            params = details.get("parameters", [])
            if params:
                md.append("| Parameters | ")
                param_list = []
                for p in params:
                    p_name = p.get("name", "")
                    p_in = p.get("in", "")
                    p_required = "Required" if p.get("required") else "Optional"
                    p_desc = p.get("description", "")
                    param_list.append(f"`{p_name}` ({p_in}, {p_required})")
                md.append(" ".join(param_list) + " |\n")

            request_body = details.get("requestBody", {})
            content = {}
            if request_body:
                content = request_body.get("content", {})
                if "application/json" in content:
                    json_schema = content["application/json"].get("schema", {})
                    schema_ref = json_schema.get("$ref", "")
                    if schema_ref:
                        schema_name = extract_ref_name(schema_ref)
                        link = f"[{schema_name}](#{schema_name.lower()})"
                        md.append(f"| Request Body | `{link}` |\n")
                    else:
                        md.append(f"| Request Body | Inline schema |\n")

            responses = details.get("responses", {})
            if responses:
                md.append("| Response | Description |\n")
                md.append("|----------|-------------|\n")
                for status_code, resp_details in responses.items():
                    resp_desc = resp_details.get("description", "")
                    md.append(f"| {status_code} | {resp_desc} |\n")

            md.append("\n")

            if request_body and "application/json" in content:
                json_schema = content["application/json"].get("schema", {})
                schema_ref = json_schema.get("$ref", "")
                if schema_ref:
                    schema_name = extract_ref_name(schema_ref)
                    schema_details = schemas.get(schema_name)
                    if schema_details:
                        example = get_schema_example(schema_details)
                        if example:
                            md.append(f"**Request Body Example:**\n")
                            md.append(f"```json\n{example}\n```\n")

            md.append("\n---\n\n")

    if schemas:
        md.append("## Data Models\n")
        for schema_name, schema_details in sorted(schemas.items()):
            md.append(f"### {schema_name}\n")

            if schema_details.get("description"):
                md.append(f"{schema_details['description']}\n")

            if "properties" in schema_details:
                md.append("| Field | Type | Description |\n")
                md.append("|-------|------|-------------|\n")

                for prop_name, prop_details in schema_details["properties"].items():
                    prop_type = prop_details.get("type", "any")
                    if "$ref" in prop_details:
                        prop_type = extract_ref_name(prop_details["$ref"])
                    elif prop_details.get("enum"):
                        prop_type = f"enum: {prop_details['enum']}"
                    elif prop_type == "array" and "items" in prop_details:
                        items_ref = prop_details["items"].get("$ref", "")
                        if items_ref:
                            prop_type = f"array[{extract_ref_name(items_ref)}]"
                        else:
                            item_type = prop_details["items"].get("type", "any")
                            prop_type = f"array[{item_type}]"

                    prop_desc = prop_details.get("description", "")
                    prop_required = " *(required)*" if prop_name in schema_details.get("required", []) else ""
                    md.append(f"| `{prop_name}` | {prop_type} | {prop_desc}{prop_required} |\n")

            md.append("\n---\n")

    return "".join(md)


def main():
    """Main function to generate and save documentation."""
    openapi_spec = get_openapi_spec()

    output_path = Path(__file__).parent.parent / "docs" / "API.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown = generate_markdown(openapi_spec)

    output_path.write_text(markdown)
    print(f"API documentation generated: {output_path}")

    json_spec_path = Path(__file__).parent.parent / "docs" / "openapi.json"
    json_spec_path.write_text(json.dumps(openapi_spec, indent=2))
    print(f"OpenAPI spec saved: {json_spec_path}")


if __name__ == "__main__":
    main()
