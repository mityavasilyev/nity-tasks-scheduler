from typing import Optional, Tuple

from injector import inject

from domain.models import TaskCreate, Task, TaskStatus, TaskType
from infrastructure.pg_repositories.engine import get_session
from infrastructure.pg_repositories.tasks_repository import TasksRepository
from utils.logger import AppLogger
from utils.time_utils import TimeUtils

logger = AppLogger.get_logger(__name__)


class TasksService:

    @inject
    def __init__(self, tasks_repository: TasksRepository):
        self.tasks_repo = tasks_repository

    async def start(self):
        """Initialize service"""
        logger.info("Tasks service started successfully")

    def stop(self):
        """Cleanup service"""
        logger.info("Tasks service stopped successfully")

    async def create_task(self, task_create: TaskCreate) -> Tuple[Optional[Task], Optional[str]]:
        """Create and enqueue a new task"""
        try:
            with get_session() as session:
                # TODO: Add check for valid task type - we can't create start_tracking task for a channel we already know

                # First, store task in database
                task = self.tasks_repo.create_task(
                    session=session,
                    message_id=TimeUtils.current_datetime().isoformat(),
                    task_type=task_create.task_type,
                    channel_id=task_create.channel_id)

                try:
                    from services.tasks_queue import enqueue_task
                    message_id = enqueue_task(task_type=task_create.task_type, channel_id=task_create.channel_id)
                    # Update task with real message ID
                    task = self.tasks_repo.update_task_message_id(session, task.id, message_id)
                    logger.info(f"Created task {task.id} of type {task.task_type} for channel {task.channel_id}")
                except ConnectionError as e:
                    # If broker is unavailable, mark task as failed
                    task = self.tasks_repo.update_task_status(session,
                                                              task.message_id,
                                                              TaskStatus.FAILED,
                                                              error_message="Failed to connect to message broker. Please try again later.")

                    logger.error(f"Failed to enqueue task {task.id} due to broker connection: {str(e)}")
                    return task, "Failed to connect to message broker. Please try again later."
                return task, None

        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            raise

    def get_task_by_status(self, channel_id: int, task_type: TaskType, task_status: TaskStatus) -> Optional[Task]:
        with get_session() as session:
            return self.tasks_repo.get_task_by_status(session=session, channel_id=channel_id, task_type=task_type,
                                                      status=task_status)
