from abc import ABC, abstractmethod
from typing import Dict, Type, Tuple, TypeVar, Awaitable, Callable

import grpclib.const
from grpclib.const import Status, Cardinality
from grpclib.exceptions import GRPCError
from grpclib.server import Stream

from domain.models import TaskType

RequestType = TypeVar('RequestType')
ResultType = TypeVar('ResultType')
ResponseType = TypeVar('ResponseType')

class BaseGrpcService(ABC):
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Service name for gRPC registration"""
        pass

    @property
    @abstractmethod
    def method_mapping(self) -> Dict[str, Tuple[str, Type, Type]]:
        """
        Dictionary mapping gRPC method names to implementation details
        Example:
        {
            "GenerateContext": ("generate_context", RequestType, ResponseType)
        }
        """
        pass

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        """Generates gRPC method mapping with handlers"""
        return {
            f"/{self.service_name}/{grpc_method}": grpclib.const.Handler(
                func=getattr(self, impl_method),
                cardinality=Cardinality.UNARY_UNARY,
                request_type=req_type,
                reply_type=resp_type
            )
            for grpc_method, (impl_method, req_type, resp_type) in self.method_mapping.items()
        }

    def handle_error(self, e: Exception) -> None:
        """Common error handling for gRPC methods"""
        if isinstance(e, ValueError):
            raise GRPCError(Status.INVALID_ARGUMENT, str(e))
        elif isinstance(e, NotImplementedError):
            raise GRPCError(Status.UNIMPLEMENTED, str(e))
        else:
            raise GRPCError(Status.INTERNAL, "Internal server error")

    async def _handle_request(
            self,
            stream: Stream[RequestType, ResponseType],
            handler: Callable[[RequestType], Awaitable[ResultType]],
            response_factory: Callable[[ResultType], ResponseType]
    ) -> None:
        """Common request handling logic"""
        try:
            request = await stream.recv_message()
            result = await handler(request)
            await stream.send_message(response_factory(result))
        except Exception as e:
            print(e)
            self.handle_error(e)