import asyncio

from dramatiq import middleware
from injector import inject

from domain.models import TaskStatus, TaskType
from infrastructure.nity.telegram_bot_client import TelegramBotClient
from infrastructure.pg_repositories.engine import get_session
from infrastructure.pg_repositories.tasks_repository import TasksRepository
from infrastructure.pg_repositories.tracked_channels_repository import TrackedChannelsRepository
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


class TaskExecutionMiddleware(middleware.Middleware):
    """Middleware to track task execution and manage channel tracking"""

    @inject
    def __init__(self, tasks_repository: TasksRepository, tracked_channels_repository: TrackedChannelsRepository,
                 telegram_bot_client: TelegramBotClient):
        self.tasks_repository = tasks_repository
        self.tracked_channels_repository = tracked_channels_repository
        self.telegram_bot_client = telegram_bot_client

    def before_process_message(self, broker, message):
        """Set task to RUNNING state"""
        logger.info(f"Starting task with message_id={message.message_id}")
        with get_session() as session:
            self.tasks_repository.update_task_status(
                session=session,
                message_id=message.message_id,
                status=TaskStatus.RUNNING
            )

    def after_process_message(self, broker, message, *, result=None, exception=None):
        """Handle task completion and channel tracking"""
        try:
            status = TaskStatus.COMPLETED if exception is None else TaskStatus.FAILED
            error_message = str(exception) if exception else None

            # Update task status
            with get_session() as session:
                updated_task = self.tasks_repository.update_task_status(
                    session=session,
                    message_id=message.message_id,
                    status=status,
                    error_message=error_message
                )
                task = self.tasks_repository.get_task_by_id(session, updated_task.id)

                if status == TaskStatus.COMPLETED:
                    if task.task_type == TaskType.START_TRACKING:

                        # Add new channel to tracking
                        channel_id = int(task.channel_id)
                        maybe_tracked_channel = self.tracked_channels_repository.get_channel(session, channel_id)
                        if maybe_tracked_channel:
                            logger.info(f"Channel {channel_id} is already tracked")
                        else:
                            self.tracked_channels_repository.add_channel(session, channel_id)
                            logger.info(f"Started tracking channel {channel_id}")
                            if task.user_id_to_notify:
                                asyncio.run(
                                    self._notify_user(
                                        nity_user_id=task.user_id_to_notify,
                                        message="Мы успешно собрали информацию по твоему каналу!"
                                    )
                                )
                                logger.info(f"Successfully notified user {task.user_id_to_notify}")

                    elif task.task_type == TaskType.REVISIT_CHANNEL:
                        # Update last revisit time
                        channel_id = int(task.channel_id)
                        self.tracked_channels_repository.update_last_revisited(session, channel_id)
                        logger.info(f"Updated last visit time for channel {channel_id}")

        except Exception as e:
            logger.error(f"Error in task completion handling: {str(e)}")
        finally:
            logger.info(f"Task with message_id={message.message_id} processing complete")


    async def _notify_user(self, nity_user_id: int, message: str):
        async with self.telegram_bot_client.connection():
            await self.telegram_bot_client.notify_nity_user(
                nity_user_id=nity_user_id,
                message=message
            )
