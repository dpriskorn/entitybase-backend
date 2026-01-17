import abc

__all__ = ["AbstractTokenProvider", "ConsumerRebalanceListener"]

class ConsumerRebalanceListener(abc.ABC, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def on_partitions_revoked(self, revoked): ...
    @abc.abstractmethod
    def on_partitions_assigned(self, assigned): ...

class AbstractTokenProvider(abc.ABC, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def token(self): ...
    def extensions(self): ...
