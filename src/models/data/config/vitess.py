"""Configuration for Vitess connections."""

from models.data.config.config import Config


class VitessConfig(Config):
    """Configuration for Vitess connections."""

    host: str
    port: int
    database: str
    user: str = "root"
    password: str = ""
