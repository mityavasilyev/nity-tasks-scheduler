from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

from betterproto import ServiceStub
from grpclib.client import Channel


@dataclass
class GrpcClientConfig:
    host: str
    port: int
    max_message_size_mb: int = 50


TStub = TypeVar('TStub', bound=ServiceStub)


class BaseGrpcClient(ABC, Generic[TStub]):
    def __init__(self, config: GrpcClientConfig):
        self.config = config
        self._channel: Optional[Channel] = None
        self._stub: Optional[TStub] = None

    @property
    @abstractmethod
    def stub_class(self) -> type[TStub]:
        """Return the betterproto stub class"""
        pass

    async def connect(self) -> None:
        """Establish connection to the gRPC server"""
        if self._channel is None:
            self._channel = Channel(
                host=self.config.host,
                port=self.config.port,
            )
            self._stub = self.stub_class(self._channel)

    async def disconnect(self) -> None:
        """Close the gRPC channel"""
        if self._channel is not None:
            self._channel.close()
            self._channel = None
            self._stub = None

    @asynccontextmanager
    async def connection(self):
        """Context manager for handling connections"""
        await self.connect()
        try:
            yield self._stub
        except Exception as e:
            print(e)
            raise e
        finally:
            await self.disconnect()

    @property
    def stub(self) -> TStub:
        if self._stub is None:
            raise RuntimeError("Client not connected")
        return self._stub
