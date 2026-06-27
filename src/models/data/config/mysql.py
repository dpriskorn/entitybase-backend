"""Configuration for Mysql connections."""

from models.data.config.config import Config


class MysqlConfig(Config):
    """Configuration for Mysql connections."""

    host: str
    port: int
    database: str
    user: str
    password: str
    pool_size: int = 10
    max_overflow: int = 10
    pool_timeout: int = 30
