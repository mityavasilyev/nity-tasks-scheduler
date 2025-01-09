from injector import Injector

from .modules import RepositoriesModule, PostgresModule, GrpcModule, ServicesModule, RabbitMqModule, \
    TasksMiddlewareModule, GrpcClientsModule


def get_container() -> Injector:
    return Injector([
        PostgresModule(),
        RepositoriesModule(),
        ServicesModule(),
        RabbitMqModule(),
        TasksMiddlewareModule(),
        GrpcModule()
    ])

def get_worker_container() -> Injector:
    return Injector([
        PostgresModule(),
        RepositoriesModule(),
        RabbitMqModule(),
        TasksMiddlewareModule(),
        GrpcClientsModule()
        ])