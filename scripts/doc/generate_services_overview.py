#!/usr/bin/env python3
"""Generate overview documentation for all services."""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List


def extract_service_info(service_file: Path) -> Dict[str, Any]:
    """Extract information from a service file."""
    info = {
        "class_name": "",
        "description": "",
        "location": str(service_file.relative_to(Path("src"))),
        "methods": [],
        "dependencies": [],
    }

    try:
        with open(service_file, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        # Find the main service class
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Service" in node.name:
                info["class_name"] = node.name
                # Get docstring
                if node.body and isinstance(node.body[0], ast.Expr):
                    expr = node.body[0]
                    if isinstance(expr.value, ast.Constant) and isinstance(
                        expr.value.value, str
                    ):
                        docstring = expr.value.value
                        info["description"] = docstring.strip()

                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and not item.name.startswith(
                        "_"
                    ):
                        method_info = {
                            "name": item.name,
                            "signature": f"{item.name}({', '.join(arg.arg for arg in item.args.args[1:])})",  # Skip 'self'
                            "description": "",
                        }
                        # Get method docstring
                    if item.body and isinstance(item.body[0], ast.Expr):
                        expr = item.body[0]
                        if isinstance(expr.value, ast.Constant) and isinstance(
                            expr.value.value, str
                        ):
                            method_doc = expr.value.value
                            method_info["description"] = method_doc.strip()
                        info["methods"].append(method_info)
                break

        # Extract dependencies from imports
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "models." in node.module:
                    for alias in node.names:
                        if not alias.name.startswith("_"):
                            info["dependencies"].append(f"{node.module}.{alias.name}")

    except Exception as e:
        print(f"Warning: Could not parse {service_file}: {e}")

    return info


def generate_markdown(services: List[Dict[str, Any]]) -> str:
    """Generate markdown overview of services."""
    lines = ["# Services Overview\n"]

    for service in services:
        lines.append(f"## {service['class_name']}\n")

        lines.append(f"**Location**: `{service['location']}`")
        lines.append(f"**Purpose**: {service['description']}\n")

        if service["methods"]:
            lines.append("**Methods**:\n")
            for method in service["methods"]:
                lines.append(f"- `{method['signature']}`")
                if method["description"]:
                    lines.append(f"  - {method['description']}")
                lines.append("")

        if service["dependencies"]:
            lines.append("**Dependencies**:\n")
            for dep in service["dependencies"]:
                lines.append(f"- `{dep}`")
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    services_dir = Path("src/models/rest_api/services")

    if not services_dir.exists():
        print("Error: Services directory not found")
        return

    services = []

    # Find all service files
    for service_file in services_dir.glob("*.py"):
        if service_file.name != "__init__.py":
            info = extract_service_info(service_file)
            if info["class_name"]:  # Only include if we found a service class
                services.append(info)

    # Sort services by name
    services.sort(key=lambda x: x["class_name"])

    # Generate markdown
    markdown = generate_markdown(services)

    # Output to stdout (will be redirected by update-docs.sh)
    print(markdown)


if __name__ == "__main__":
    main()
