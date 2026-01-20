from models.infrastructure.config import Config


class StreamConfig(Config):
    bootstrap_servers: str
    topic: str