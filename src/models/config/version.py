"""Application version constants."""

import os
import tomllib
from importlib.metadata import version
from pathlib import Path

from typing import Any


def get_pyproject_path() -> Path:
    """Get path to pyproject.toml based on environment."""
    possible_paths = [
        Path("/app/pyproject.toml"),
        Path(__file__).parent.parent.parent.parent / "pyproject.toml",
        Path.cwd() / "pyproject.toml",
    ]
    for path in possible_paths:
        if path.exists():
            return path
    raise FileNotFoundError(f"pyproject.toml not found in any of: {possible_paths}")


def get_release_version() -> str:
    """Get release version from pyproject.toml."""
    try:
        return version("entitybase-backend")
    except Exception:
        pass

    try:
        pyproject_path = get_pyproject_path()
        with open(pyproject_path, "rb") as f:
            data: Any = tomllib.load(f)
        raw_version: str = data["project"]["version"]
        return raw_version.lstrip("v")
    except Exception:
        raise RuntimeError(
            "Could not determine release version. "
            "Either install the package ('poetry install') or ensure pyproject.toml is readable."
        )


def get_api_version() -> str:
    """Get full API.release_version) from version (api_version pyproject.toml."""
    try:
        pyproject_path = get_pyproject_path()
        with open(pyproject_path, "rb") as f:
            data: Any = tomllib.load(f)
        api_version: str = data["project"]["api_version"]
        release_version: str = get_release_version()
        return f"{api_version}.{release_version}"
    except Exception as e:
        raise RuntimeError(
            f"Could not determine API version: {e}. "
            "Ensure pyproject.toml has 'api_version' and 'version' fields in [project] section."
        )


def get_entitybase_version() -> str:
    """Get entitybase version from pyproject.toml."""
    return get_release_version()


API_VERSION = get_api_version()
ENTITYBASE_VERSION = get_entitybase_version()
