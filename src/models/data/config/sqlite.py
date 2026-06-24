"""Configuration for SQLite connections."""

from pathlib import Path

from models.data.config.config import Config


class SqliteConfig(Config):
    """Configuration for SQLite connections."""

    datadir: Path
