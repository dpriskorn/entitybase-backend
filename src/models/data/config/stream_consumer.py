"""Stream consumer configuration."""

from models.data.config.config import Config


class StreamConsumerConfig(Config):
    """Configuration for Kafka stream consumer."""

    brokers: list[str]
    topic: str
    group_id: str = "watchlist-consumer"