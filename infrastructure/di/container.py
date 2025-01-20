from injector import Injector

from .modules import RepositoriesModule, GrpcModule, ServicesModule, RabbitMqModule, \
    TasksMiddlewareModule, GrpcClientsModule


def get_container() -> Injector:
    return Injector([
        RepositoriesModule(),
        ServicesModule(),
        RabbitMqModule(),
        TasksMiddlewareModule(),
        GrpcModule()
    ])


def get_worker_container() -> Injector:
    return Injector([
        RepositoriesModule(),
        RabbitMqModule(),
        TasksMiddlewareModule(),
        GrpcClientsModule()
    ])
