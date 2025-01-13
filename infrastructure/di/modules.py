from injector import Module, singleton, provider
from sqlalchemy.orm import Session

from api.base_server import GrpcServerConfig
from api.server import TasksGrpcServer
from api.service import TasksGrpcService
from config import settings
from infrastructure.nity.channel_intelligence_client import ChannelIntelligenceConfig, ChannelIntelligenceClient
from infrastructure.pg_repositories.engine import Session as SQLAlchemySession
from infrastructure.pg_repositories.tasks_repository import TasksRepository
from infrastructure.pg_repositories.tracked_channels_repository import TrackedChannelsRepository
from infrastructure.rabbitmq.broker_client import BrokerClient
from services.tasks_service import TasksService


class PostgresModule(Module):
    @provider
    @singleton
    def provide_session(self) -> Session:
        return SQLAlchemySession()


class RabbitMqModule(Module):
    @provider
    @singleton
    def provide_rabbitmq_connection(self) -> BrokerClient:
        return BrokerClient()


class ServicesModule(Module):

    @provider
    @singleton
    def provide_tasks_service(self, tasks_repository: TasksRepository) -> TasksService:
        return TasksService(tasks_repository)


class RepositoriesModule(Module):

    @provider
    @singleton
    def provide_tasks_repository(self, session: Session) -> TasksRepository:
        return TasksRepository(session)

    @provider
    @singleton
    def provide_tracked_channels_repository(self, session: Session) -> TrackedChannelsRepository:
        return TrackedChannelsRepository(session)


class GrpcModule(Module):

    @provider
    @singleton
    def provide_grpc_server_config(self) -> GrpcServerConfig:
        return GrpcServerConfig(port=settings.GRPC_SERVER_PORT)

    @provider
    @singleton
    def provide_tasks_grpc_service(self, tasks_service: TasksService) -> TasksGrpcService:
        return TasksGrpcService(tasks_service=tasks_service)

    @provider
    @singleton
    def provide_grpc_server(self, config: GrpcServerConfig,
                            tasks_grpc_service: TasksGrpcService) -> TasksGrpcServer:
        return TasksGrpcServer(config, tasks_grpc_service)


class GrpcClientsModule(Module):
    @provider
    @singleton
    def provide_channel_intelligence_config(self) -> ChannelIntelligenceConfig:
        return ChannelIntelligenceConfig(
            host=settings.CHANNEL_INTELLIGENCE_GRPC_HOST,
            port=settings.CHANNEL_INTELLIGENCE_GRPC_PORT
        )

    @provider
    @singleton
    def provide_channel_intelligence_client(
            self,
            config: ChannelIntelligenceConfig
    ) -> ChannelIntelligenceClient:
        return ChannelIntelligenceClient(config)


class TasksMiddlewareModule(Module):

    @provider
    @singleton
    def provide_tasks_middleware(self, tasks_service: TasksService) -> TasksGrpcService:
        return TasksGrpcService(tasks_service=tasks_service)
