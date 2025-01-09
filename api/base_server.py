from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

from grpclib.reflection.service import ServerReflection
from grpclib.server import Server

from utils.logger import AppLogger


@dataclass
class GrpcServerConfig:
    port: int = 50051
    host: str = "127.0.0.1"


TService = TypeVar('TService')


class BaseGrpcServer(ABC, Generic[TService]):
    def __init__(self, config: GrpcServerConfig):
        self.config = config
        self._server: Optional[Server] = None
        self._logger = AppLogger.get_logger(self.__class__.__name__)

    @property
    @abstractmethod
    def service(self) -> [TService]:
        """Return the service implementation"""
        pass

    @property
    @abstractmethod
    def service_names(self) -> list[str]:
        """Return the list of service names for reflection"""
        pass

    async def start(self) -> None:
        """Start the gRPC server"""
        try:
            services = self.service
            services = ServerReflection.extend(services)

            self._server = Server(services)
            await self._server.start(self.config.host, self.config.port)

            self._logger.info(f"Server started at {self.config.host}:{self.config.port}")
        except Exception as e:
            self._logger.error(f"Failed to start server: {str(e)}")
            raise

    async def stop(self) -> None:
        """Stop the gRPC server"""
        if self._server:
            try:
                self._server.close()
                await self._server.wait_closed()
                self._logger.info("Server stopped")
            except Exception as e:
                self._logger.error(f"Error stopping server: {str(e)}")
                raise

    async def serve(self) -> None:
        """Run the server until interrupted"""
        await self.start()
        try:
            await self._server.wait_closed()
        finally:
            await self.stop()
