#!/usr/bin/env python3
"""Generate overview documentation for repository classes."""

import ast
from pathlib import Path
from typing import Dict, Any, List


def extract_repository_info(repo_file: Path) -> Dict[str, Any]:
    """Extract information from a repository file."""
    info = {
        "class_name": "",
        "description": "",
        "location": str(repo_file.relative_to(Path("src"))),
        "methods": [],
    }

    try:
        with open(repo_file, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        # Find the main repository class
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Repository" in node.name:
                info["class_name"] = node.name
                # Get docstring
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, (ast.Str, ast.Constant))
                ):
                    if isinstance(node.body[0].value, ast.Str):
                        docstring = node.body[0].value.s
                    else:
                        docstring = node.body[0].value.value
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
                            "return_type": "None",
                        }

                        # Get return type
                        if item.returns:
                            method_info["return_type"] = ast.unparse(item.returns)

                        # Get method docstring
                        if (
                            item.body
                            and isinstance(item.body[0], ast.Expr)
                            and isinstance(item.body[0].value, (ast.Str, ast.Constant))
                        ):
                            if isinstance(item.body[0].value, ast.Str):
                                method_doc = item.body[0].value.s
                            else:
                                method_doc = item.body[0].value.value
                            method_info["description"] = method_doc.strip()

                        info["methods"].append(method_info)
                break

    except Exception as e:
        print(f"Warning: Could not parse {repo_file}: {e}")

    return info


def generate_markdown(repositories: List[Dict[str, Any]]) -> str:
    """Generate markdown overview of repositories."""
    lines = ["# Repository Classes Overview\n"]

    lines.append(
        "This document describes the repository classes that handle data access to Vitess.\n"
    )

    # Group repositories by functionality
    grouped = {
        "Core Entity Operations": [],
        "Backlinks": [],
        "Statements": [],
        "Metadata": [],
        "Other": [],
    }

    for repo in repositories:
        name_lower = repo["class_name"].lower()
        if "entity" in name_lower and "repository" in name_lower:
            grouped["Core Entity Operations"].append(repo)
        elif "backlink" in name_lower:
            grouped["Backlinks"].append(repo)
        elif "statement" in name_lower:
            grouped["Statements"].append(repo)
        elif "metadata" in name_lower:
            grouped["Metadata"].append(repo)
        else:
            grouped["Other"].append(repo)

    # Generate documentation by group
    for group_name, repos in grouped.items():
        if not repos:
            continue

        lines.append(f"## {group_name}\n")

        for repo in repos:
            lines.append(f"### {repo['class_name']}\n")

            lines.append(f"**Location**: `{repo['location']}`")
            lines.append(f"**Purpose**: {repo['description']}\n")

            if repo["methods"]:
                lines.append("**Methods**:\n")
                for method in repo["methods"]:
                    lines.append(
                        f"- `{method['signature']} -> {method['return_type']}`"
                    )
                    if method["description"]:
                        lines.append(f"  - {method['description']}")
                    lines.append("")

    # Architecture notes
    lines.append("## Architecture Notes\n")
    lines.append(
        "- **Connection Management**: All repositories receive a `connection_manager` for database access"
    )
    lines.append(
        "- **Transaction Safety**: Methods should be called within connection contexts"
    )
    lines.append(
        "- **Error Handling**: Repositories raise exceptions for database errors"
    )
    lines.append("- **Performance**: Methods are optimized for common query patterns")
    lines.append(
        "- **Data Integrity**: Foreign key relationships are maintained at the application level"
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    repo_dir = Path("src/models/infrastructure/vitess")

    if not repo_dir.exists():
        print("Error: Repository directory not found")
        return

    repositories = []

    # Find all repository files (exclude schema.py and __init__.py)
    for repo_file in repo_dir.glob("*.py"):
        if (
            repo_file.name not in ["schema.py", "__init__.py"]
            and "repository" in repo_file.name.lower()
        ):
            info = extract_repository_info(repo_file)
            if info["class_name"]:  # Only include if we found a repository class
                repositories.append(info)

    # Sort repositories by class name
    repositories.sort(key=lambda x: x["class_name"])

    # Generate markdown
    markdown = generate_markdown(repositories)

    # Output to stdout (will be redirected by update-docs.sh)
    print(markdown)


if __name__ == "__main__":
    main()
