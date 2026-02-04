#!/usr/bin/env python3
"""Test API models generation."""
from pathlib import Path
from scripts.doc.generate_api_models_overview import extract_model_info, generate_markdown

# Test path
response_dir = Path("src/models/data/rest_api/v1/entitybase/response")
print(f"Response dir exists: {response_dir.exists()}")
print(f"Response dir path: {response_dir.absolute()}")

if response_dir.exists():
    all_models = []
    for model_file in response_dir.rglob("*.py"):
        if model_file.name != "__init__.py":
            print(f"Processing: {model_file}")
            models = extract_model_info(model_file)
            all_models.extend(models)

    print(f"Found {len(all_models)} models")
    for model in all_models[:5]:
        print(f"  - {model['class_name']}")
else:
    print("ERROR: Directory does not exist")
