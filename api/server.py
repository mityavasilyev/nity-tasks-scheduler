from injector import inject

from api.base_server import BaseGrpcServer, GrpcServerConfig
from api.base_service import BaseGrpcService
from api.service import TasksGrpcService


class TasksGrpcServer(BaseGrpcServer[TasksGrpcService]):

    @inject
    def __init__(self, config: GrpcServerConfig, suggestions_grpc_server: TasksGrpcService):
        super().__init__(config)
        self._suggestions_service = suggestions_grpc_server

    @property
    def service(self) -> [BaseGrpcService]:
        return [self._suggestions_service]

    @property
    def service_names(self) -> list[str]:
        return [
            "suggestions.SuggestionsService",
            "grpc.reflection.v1alpha.ServerReflection"
        ]
