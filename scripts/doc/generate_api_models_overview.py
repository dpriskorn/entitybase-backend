#!/usr/bin/env python3
"""Generate overview documentation for API response models."""

import ast
from pathlib import Path
from typing import Dict, Any, List


# noinspection PyUnresolvedReferences
def extract_model_info(model_file: Path) -> List[Dict[str, Any]]:
    """Extract information from a models file."""
    models = []

    try:
        with open(model_file, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and any(
                base.id == "BaseModel"
                for base in node.bases
                if isinstance(base, ast.Name)
            ):
                model_info = {
                    "class_name": node.name,
                    "location": str(model_file.relative_to(Path("src"))),
                    "description": "",
                    "fields": [],
                }

                # Get class docstring
                if node.body and isinstance(node.body[0], ast.Expr):
                    expr = node.body[0]
                    if isinstance(expr.value, ast.Constant) and isinstance(
                        expr.value.value, str
                    ):
                        docstring = expr.value.value
                        model_info["description"] = docstring.strip()

                # Extract fields
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and item.target.id not in [
                        "model_config"
                    ]:
                        field_name = item.target.id
                        field_type = "Unknown"
                        field_description = ""

                        # Get field type annotation
                        if item.annotation:
                            field_type = ast.unparse(item.annotation)

                        # Get field description from comments or default values
                        if item.value and isinstance(item.value, ast.Call):
                            # Look for Field() calls
                            for arg in item.value.args:
                                if isinstance(arg, ast.Constant) and isinstance(
                                    arg.value, str
                                ):
                                    field_description = arg.value
                                    break
                            # Look for keyword arguments
                            for keyword in item.value.keywords:
                                if (
                                    keyword.arg == "description"
                                    and isinstance(keyword.value, ast.Constant)
                                    and isinstance(keyword.value.value, str)
                                ):
                                    field_description = keyword.value.value
                                    break

                        model_info["fields"].append(
                            {
                                "name": field_name,
                                "type": field_type,
                                "description": field_description,
                            }
                        )

                models.append(model_info)

    except Exception as e:
        print(f"Warning: Could not parse {model_file}: {e}")

    return models


def generate_markdown(models: List[Dict[str, Any]]) -> str:
    """Generate markdown overview of API models."""
    lines = ["# API Models Overview\n"]

    # Group models by file
    models_by_file = {}
    for model in models:
        file_path = model["location"]
        if file_path not in models_by_file:
            models_by_file[file_path] = []
        models_by_file[file_path].append(model)

    # Sort files
    for file_path in sorted(models_by_file.keys()):
        lines.append(f"## {file_path}\n")

        for model in models_by_file[file_path]:
            lines.append(f"### {model['class_name']}\n")

            if model["description"]:
                lines.append(f"{model['description']}\n")

            if model["fields"]:
                lines.append("**Fields**:\n")
                for field in model["fields"]:
                    lines.append(
                        f"- `{field['name']}` ({field['type']}): {field['description'] or 'No description'}"
                    )
                lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    response_dir = Path("src/models/data/rest_api/v1/entitybase/response")

    if not response_dir.exists():
        print("Error: Response models directory not found")
        return

    all_models = []

    # Find all response model files
    for model_file in response_dir.rglob("*.py"):
        if model_file.name != "__init__.py":
            models = extract_model_info(model_file)
            all_models.extend(models)

    # Sort models by class name
    all_models.sort(key=lambda x: x["class_name"])

    # Generate markdown
    markdown = generate_markdown(all_models)

    # Output to stdout (will be redirected by update-docs.sh)
    print(markdown)


if __name__ == "__main__":
    main()
