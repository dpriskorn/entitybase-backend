"""Stream consumer configuration."""

from models.data.config.config import Config


class StreamConsumerConfig(Config):
    """Configuration for Kafka stream consumer."""

    brokers: list[str]
    topic: str = "wikibase-entity-changes"
    group_id: str = "watchlist-consumer"
    auto_offset_reset: str = "latest"
