from dramatiq import middleware
from injector import inject

from domain.models import TaskStatus, TaskType
from infrastructure.pg_repositories.tasks_repository import TasksRepository
from infrastructure.pg_repositories.tracked_channels_repository import TrackedChannelsRepository
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


class TaskExecutionMiddleware(middleware.Middleware):
    """Middleware to track task execution and manage channel tracking"""

    @inject
    def __init__(self, tasks_repository: TasksRepository, tracked_channels_repository: TrackedChannelsRepository):
        self.tasks_repository = tasks_repository
        self.tracked_channels_repository = tracked_channels_repository

    def before_process_message(self, broker, message):
        """Set task to RUNNING state"""
        logger.info(f"Starting task {message.message_id}")
        self.tasks_repository.update_task_status(
            message_id=message.message_id,
            status=TaskStatus.RUNNING
        )

    def after_process_message(self, broker, message, *, result=None, exception=None):
        """Handle task completion and channel tracking"""
        try:
            status = TaskStatus.COMPLETED if exception is None else TaskStatus.FAILED
            error_message = str(exception) if exception else None

            # Update task status
            task = self.tasks_repository.update_task_status(
                message_id=message.message_id,
                status=status,
                error_message=error_message
            )

            if status == TaskStatus.COMPLETED:
                if task.task_type == TaskType.START_TRACKING:
                    # Add new channel to tracking
                    channel_id = int(task.channel_id)
                    self.tracked_channels_repository.add_channel(channel_id)
                    logger.info(f"Started tracking channel {channel_id}")

                elif task.task_type == TaskType.REVISIT_CHANNEL:
                    # Update last revisit time
                    channel_id = int(task.channel_id)
                    self.tracked_channels_repository.update_last_revisited(channel_id)
                    logger.info(f"Updated last visit time for channel {channel_id}")

        except Exception as e:
            logger.error(f"Error in task completion handling: {str(e)}")
        finally:
            logger.info(f"Task {message.message_id} processing complete")
