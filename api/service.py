from typing import Tuple, Optional

from grpclib.server import Stream
from injector import inject

from api.base_service import BaseGrpcService
from api.proto.tasks import CreateTaskRequest, CreateTaskResponse, GetTaskRequest, GetTaskResponse, \
    GetChannelTasksRequest, GetChannelTasksResponse, CreateTaskWithUserNotificationRequest
from domain.models import Task, TaskCreate, TaskType
from services.tasks_service import TasksService
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)

import api.proto.tasks_service_pb2 as reflection_data

logger.info("Loaded gRPC server reflection data for " + reflection_data.__name__)


class TasksGrpcService(BaseGrpcService):

    @property
    def service_name(self) -> str:
        return "tasks.TasksService"

    @property
    def method_mapping(self):
        return {
            "CreateTask": ("create_task", CreateTaskRequest, CreateTaskResponse),
            "GetTask": ("get_task", GetTaskRequest, GetTaskResponse),
            "GetChannelTasks": ("get_channel_tasks", GetTaskRequest, GetTaskResponse),
            "CreateTaskWithUserNotification": ("create_task_with_user_notification", CreateTaskWithUserNotificationRequest, CreateTaskResponse),
        }

    @inject
    def __init__(self, tasks_service: TasksService):
        self.tasks_service = tasks_service
        logger.info("tasks.TasksService gRPC service initialized")

    async def create_task(self, stream: Stream[CreateTaskRequest, CreateTaskResponse]) -> None:
        async def handler(req: CreateTaskRequest) -> Tuple[Optional[Task], Optional[str]]:
            return await self.tasks_service.create_task(
                TaskCreate(channel_id=req.channel_id, task_type=self._task_type_from_proto(req.task_type)))

        def response_factory(result: Tuple[Optional[Task], Optional[str]]) -> CreateTaskResponse:
            task, error = result
            if error:
                raise Exception(error)
            return CreateTaskResponse(task_id=task.id, error_message="")

        await self._handle_request(
            stream=stream,
            handler=handler,
            response_factory=response_factory
        )

    async def create_task_with_user_notification(self, stream: Stream[CreateTaskWithUserNotificationRequest, CreateTaskResponse]) -> None:
        async def handler(req: CreateTaskWithUserNotificationRequest) -> Tuple[Optional[Task], Optional[str]]:
            return await self.tasks_service.create_task(
                TaskCreate(
                    channel_id=req.channel_id,
                    task_type=self._task_type_from_proto(req.task_type),
                ),
                user_id_to_notify=req.user_id_to_notify
            )

        def response_factory(result: Tuple[Optional[Task], Optional[str]]) -> CreateTaskResponse:
            task, error = result
            if error:
                raise Exception(error)
            return CreateTaskResponse(task_id=task.id, error_message="")

        await self._handle_request(
            stream=stream,
            handler=handler,
            response_factory=response_factory
        )


    async def get_task(self, stream: Stream[GetTaskRequest, GetTaskResponse]) -> None:
        pass

    async def get_channel_tasks(self, stream: Stream[GetChannelTasksRequest, GetChannelTasksResponse]) -> None:
        pass

    def _task_type_from_proto(self, task_type: int) -> TaskType:
        if task_type == 0:
            return TaskType.START_TRACKING
        elif task_type == 1:
            return TaskType.REVISIT_CHANNEL
