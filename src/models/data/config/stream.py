from models.data.config.config import Config


class StreamConfig(Config):
    bootstrap_servers: str
    topic: str
