"""Configuration for MySQL-compatible database connections (Vitess, MariaDB)."""

from models.data.config.config import Config


class MysqlConfig(Config):
    """Configuration for MySQL-compatible database connections."""

    host: str
    port: int
    database: str
    user: str
    password: str
    pool_size: int = 10
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_enabled: bool = False
    bulk_import_mode: bool = False


# Backward compatibility alias
VitessConfig = MysqlConfig
