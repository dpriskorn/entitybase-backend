"""Checksum utilities."""

import hashlib
from pathlib import Path


def generate_file_sha256(filepath: Path) -> str:
    """Generate SHA-256 checksum for a file in chunks.

    Args:
        filepath: Path to the file to checksum.

    Returns:
        Hexadecimal SHA-256 digest string.
    """
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
