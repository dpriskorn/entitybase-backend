"""Application version constants."""

import tomllib
from importlib.metadata import version
from pathlib import Path

from typing import Any


def get_api_version() -> str:
    """Get API version from pyproject.toml."""
    try:
        return version("entitybase-backend")
    except Exception:
        pass

    try:
        pyproject_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data: Any = tomllib.load(f)
        return data["project"]["version"]  # type: ignore[no-any-return]
    except Exception:
        raise RuntimeError(
            "Could not determine API version. "
            "Either install the package ('poetry install') or ensure pyproject.toml is readable."
        )


def get_entitybase_version() -> str:
    """Get entitybase version from pyproject.toml."""
    return get_api_version()


API_VERSION = get_api_version()
ENTITYBASE_VERSION = get_entitybase_version()
