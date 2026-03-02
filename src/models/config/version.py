"""Application version constants."""

import tomllib
from importlib.metadata import version
from pathlib import Path

from typing import Any


def get_release_version() -> str:
    """Get release version from pyproject.toml."""
    try:
        return version("entitybase-backend")
    except Exception:
        pass

    # Try Docker path first, then fall back to project root
    for pyproject_path in [
        Path("/app/pyproject.toml"),
        Path(__file__).parent.parent.parent.parent / "pyproject.toml",
    ]:
        try:
            with open(pyproject_path, "rb") as f:
                data: Any = tomllib.load(f)
            raw_version: str = data["project"]["version"]
            return raw_version.lstrip("v")
        except Exception:
            continue

    raise RuntimeError(
        "Could not determine release version. "
        "Either install the package ('poetry install') or ensure pyproject.toml is readable."
    )


def get_api_version() -> str:
    """Get full API version (api_version.release_version) from pyproject.toml."""
    # Try Docker path first, then fall back to project root
    for pyproject_path in [
        Path("/app/pyproject.toml"),
        Path(__file__).parent.parent.parent.parent / "pyproject.toml",
    ]:
        try:
            with open(pyproject_path, "rb") as f:
                data: Any = tomllib.load(f)
            api_version: str = data["project"]["api_version"]
            release_version: str = get_release_version()
            return f"{api_version}.{release_version}"
        except Exception:
            continue

    raise RuntimeError(
        "Could not determine API version. "
        "Ensure pyproject.toml has 'api_version' and 'version' fields in [project] section."
    )


def get_entitybase_version() -> str:
    """Get entitybase version from pyproject.toml."""
    return get_release_version()


API_VERSION = get_api_version()
ENTITYBASE_VERSION = get_entitybase_version()
