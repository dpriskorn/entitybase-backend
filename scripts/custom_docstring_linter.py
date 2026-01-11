#!/usr/bin/env python3
"""Custom docstring linter that skips enums and frozen Pydantic models."""

import ast
import sys
from pathlib import Path
from typing import List, Set

# Configuration
CHECK_GOOGLE_STYLE_ARGS_RETURNS = False

# Allowlist: paths to skip docstring checking (relative to src/)
ALLOWLIST_PATHS = [
    "models/rest_api/wikibase/*",
    "models/rest_api/entitybase/*",
    "models/rest_api/response/*",
    "models/rest_api/request/*",
]


def is_enum_class(node: ast.ClassDef) -> bool:
    """Check if a class is an Enum."""
    return any(
        (isinstance(base, ast.Name) and base.id == "Enum")
        or (isinstance(base, ast.Attribute) and base.attr == "Enum")
        for base in node.bases
    )


def is_frozen_model(node: ast.ClassDef) -> bool:
    """Check if a class is a frozen Pydantic model."""
    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and target.id == "model_config":
                    # Check if it's ConfigDict(frozen=True)
                    if isinstance(item.value, ast.Call):
                        for kw in item.value.keywords:
                            if (
                                kw.arg == "frozen"
                                and isinstance(kw.value, ast.Constant)
                                and kw.value.value is True
                            ):
                                return True
                    break
    return False


def get_docstring(node: ast.AST) -> str | None:
    """Extract docstring from an AST node."""
    return ast.get_docstring(node)


def check_docstring_format(docstring: str, node: ast.AST) -> List[str]:  # type: ignore[misc]
    """Check docstring format against Google-style pydocstyle rules."""
    errors = []
    if not docstring:
        return errors

    lines = docstring.splitlines()
    num_lines = len(lines)

    # For one-liners, accept as good-enough (no D415 or D205 checks)
    if num_lines == 1:
        return errors

    if lines:
        first_line = lines[0].strip()
        if not first_line:
            return errors  # Empty first line, but docstring exists
        # D415: First line should end with punctuation
        if not first_line.endswith((".", "!", "?")):
            errors.append(
                "D415 First line should end with a period, question mark, or exclamation point"
            )

    # D205: 1 blank line required between summary line and description
    if num_lines > 1:
        summary_end = 0
        for i, line in enumerate(lines):
            if line.strip():
                summary_end = i
            elif i == summary_end + 1:
                break
        if summary_end + 1 < num_lines and lines[summary_end + 1].strip():
            errors.append(
                "D205 1 blank line required between summary line and description"
            )

    # Google-style checks
    if CHECK_GOOGLE_STYLE_ARGS_RETURNS:
        doc_lower = docstring.lower()
        has_args_section = "args:" in doc_lower
        has_returns_section = "returns:" in doc_lower

        if isinstance(node, ast.FunctionDef):
            # Check if function has parameters (excluding 'self' for methods)
            params = [arg.arg for arg in node.args.args if arg.arg != "self"]
            if params and not has_args_section:
                errors.append(
                    "Google-style: Missing 'Args:' section for function with parameters"
                )
            if node.returns and not has_returns_section:
                errors.append(
                    "Google-style: Missing 'Returns:' section for function with return annotation"
                )

    return errors

    lines = docstring.splitlines()
    if lines:
        first_line = lines[0].strip()
        if not first_line:
            return errors  # Empty first line, but docstring exists
        # D415: First line should end with punctuation
        if not first_line.endswith((".", "!", "?")):
            errors.append(
                "D415 First line should end with a period, question mark, or exclamation point"
            )

    # D205: 1 blank line required between summary and description
    if len(lines) > 1:
        summary_end = 0
        for i, line in enumerate(lines):
            if line.strip():
                summary_end = i
            elif i == summary_end + 1:
                break
        if summary_end + 1 < len(lines) and lines[summary_end + 1].strip():
            errors.append(
                "D205 1 blank line required between summary line and description"
            )

    return errors


def check_file(file_path: Path) -> List[str]:
    """Check a single file for docstring issues, skipping enums and frozen models."""
    # Check allowlist
    relative_str = str(file_path.relative_to(Path("src")))
    for pattern in ALLOWLIST_PATHS:
        if relative_str.startswith(pattern.rstrip("*")):
            return []  # Skip this file

    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return [f"{file_path}:1:1: E999 SyntaxError in file"]

    # Check for TYPE_CHECKING pass blocks
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            if (
                isinstance(node.test, ast.Name)
                and node.test.id == "TYPE_CHECKING"
                and len(node.body) == 1
                and isinstance(node.body[0], ast.Pass)
            ):
                errors.append(
                    f"{file_path}:{node.lineno}:1: Unnecessary TYPE_CHECKING pass block - remove it"
                )

    # Set parent for class methods first
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            setattr(child, "_parent", node)

    skipped_classes: Set[str] = set()
    has_skipped = False

    # First pass: identify skipped classes
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if is_enum_class(node) or is_frozen_model(node):
                skipped_classes.add(node.name)
                has_skipped = True

    module_docstring = ast.get_docstring(tree)  # type: ignore[arg-type]

    # D100: Missing docstring in public module
    if not module_docstring and not has_skipped:
        errors.append(f"{file_path}:1:1: D100 Missing docstring in public module")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if is_enum_class(node) or is_frozen_model(node):
                continue
            # D101: Missing docstring in public class
            if not node.name.startswith("_"):
                doc = get_docstring(node)  # type: ignore[arg-type]
                if not doc:
                    errors.append(
                        f"{file_path}:{node.lineno}:1: D101 Missing docstring in public class '{node.name}'"
                    )
                else:
                    format_errors = check_docstring_format(doc, node)
                    for err in format_errors:
                        errors.append(f"{file_path}:{node.lineno}:1: {err}")

        elif isinstance(node, ast.FunctionDef):
            # Skip if inside a skipped class
            parent = getattr(node, "_parent", None)
            if (
                parent
                and isinstance(parent, ast.ClassDef)
                and parent.name in skipped_classes
            ):
                continue
            # D103: Missing docstring in public function
            if not node.name.startswith("_"):
                doc = get_docstring(node)  # type: ignore[arg-type]
                if not doc:
                    kind = (
                        "method"
                        if parent and isinstance(parent, ast.ClassDef)
                        else "function"
                    )
                    code = "D102" if kind == "method" else "D103"
                    errors.append(
                        f"{file_path}:{node.lineno}:1: {code} Missing docstring in public {kind} '{node.name}'"
                    )
                else:
                    format_errors = check_docstring_format(doc, node)
                    for err in format_errors:
                        errors.append(f"{file_path}:{node.lineno}:1: {err}")

    return errors


def main() -> int:
    """Main entry point."""
    src_dir = Path("src")
    if not src_dir.exists():
        print("Error: src/ directory not found", file=sys.stderr)
        return 1

    all_errors = []
    for py_file in src_dir.rglob("*.py"):
        # Skip tests and scripts
        if "tests" in py_file.parts or "scripts" in py_file.parts:
            continue
        errors = check_file(py_file)
        all_errors.extend(errors)

    for error in all_errors:
        print(error)

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
