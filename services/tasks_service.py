from typing import List, Optional, Tuple

from injector import inject

from domain.models import TaskCreate, Task, TaskStatus
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
            # TODO: Add check for valid task type - we can't create start_tracking task for a channel we already know

            # First, store task in database
            task = self.tasks_repo.create_task(
                message_id=TimeUtils.current_datetime().isoformat(),
                task_type=task_create.task_type,
                channel_id=task_create.channel_id)

            try:
                from services.tasks_queue import enqueue_task
                message_id = enqueue_task(task_type=task_create.task_type, channel_id=task_create.channel_id)
                # Update task with real message ID
                task = self.tasks_repo.update_task_message_id(task.id, message_id)
                logger.info(f"Created task {task.id} of type {task.task_type} for channel {task.channel_id}")
            except ConnectionError as e:
                # If broker is unavailable, mark task as failed
                task = self.tasks_repo.update_task_status(
                    task.message_id,
                    TaskStatus.FAILED,
                    error_message="Failed to connect to message broker. Please try again later.")

                logger.error(f"Failed to enqueue task {task.id} due to broker connection: {str(e)}")
                return task, "Failed to connect to message broker. Please try again later."
            return task, None

        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            raise

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks_repo.get_task_by_id(task_id)

    def get_tasks_by_status(self, task_status: TaskStatus) -> List[Task]:
        """Get all tasks with specified status"""
        return self.tasks_repo.get_tasks_by_status(task_status)

    def get_channel_tasks(self, channel_id: int) -> List[Task]:
        """Get all tasks for a specific channel"""
        return self.tasks_repo.get_tasks_by_channel(channel_id)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return self.tasks_repo.get_all_tasks()
