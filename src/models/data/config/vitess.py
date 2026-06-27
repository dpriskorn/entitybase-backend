"""Configuration for Vitess connections."""

from models.data.config.config import Config


class VitessConfig(Config):
    """Configuration for Vitess connections."""

    host: str
    port: int
    database: str
    user: str
    password: str
    pool_size: int = 10
    max_overflow: int = 10
    pool_timeout: int = 30
