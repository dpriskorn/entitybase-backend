from models.data.config.config import Config


class StreamConfig(Config):
    bootstrap_servers: list[str]
    topic: str
