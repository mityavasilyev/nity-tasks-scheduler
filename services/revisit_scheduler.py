import asyncio
import traceback

from injector import inject

from config import settings
from domain.models import TaskCreate, TaskType, TaskStatus
from infrastructure.pg_repositories.engine import get_session
from infrastructure.pg_repositories.tracked_channels_repository import TrackedChannelsRepository
from services.tasks_service import TasksService
from utils.logger import AppLogger
from utils.time_utils import TimeUtils

logger = AppLogger.get_logger(__name__)


class RevisitScheduler:

    @inject
    def __init__(self, repository: TrackedChannelsRepository, tasks_service: TasksService):
        self.repository = repository
        self.tasks_service = tasks_service
        self._running = False
        self._last_run = None

    async def start(self):
        """Start the scheduler loop"""
        self._running = True
        while self._running:
            try:
                logger.info("Starting revisit scheduler loop")
                await self._process_due_channels()
                self._last_run = TimeUtils.current_datetime()
                # Wait for next interval
                await asyncio.sleep(settings.REVISIT_CHECK_INTERVAL_SECONDS)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                # Wait a bit before retrying
                traceback.print_exc()
                await asyncio.sleep(5)

    def stop(self):
        """Stop the scheduler loop"""
        self._running = False

    async def _process_due_channels(self):
        """Process all channels that are due for revisit"""
        try:
            # Get channels that need revisiting based on interval
            with get_session() as session:
                channels = self.repository.get_channels_due_revisit(
                    session=session,
                    interval_minutes=settings.REVISIT_INTERVAL_MINUTES
                )

                for channel in channels:
                    try:
                        # Create revisit task using TasksService
                        maybe_pending_task = self.tasks_service.get_task_by_status(channel_id=channel.channel_id,
                                                                                   task_type=TaskType.REVISIT_CHANNEL,
                                                                                   task_status=TaskStatus.PENDING)
                        if maybe_pending_task:
                            logger.info(f"Revisit task for channel {channel.channel_id} is already pending")
                            continue

                        maybe_failed_task = self.tasks_service.get_task_by_status(channel_id=channel.channel_id,
                                                                                  task_type=TaskType.REVISIT_CHANNEL,
                                                                                  task_status=TaskStatus.FAILED)
                        if maybe_failed_task:
                            logger.info(f"Revisit task for channel {channel.channel_id} was failed. It will be retried")
                            continue

                        maybe_running_task = self.tasks_service.get_task_by_status(channel_id=channel.channel_id,
                                                                                   task_type=TaskType.REVISIT_CHANNEL,
                                                                                   task_status=TaskStatus.RUNNING)
                        if maybe_running_task:
                            logger.info(f"Revisit task for channel {channel.channel_id} is already running")
                            continue

                        task, error = await self.tasks_service.create_task(
                            TaskCreate(
                                task_type=TaskType.REVISIT_CHANNEL,
                                channel_id=channel.channel_id
                            )
                        )
                        logger.info(
                            f"Created revisit task {task.id} for channel {channel.channel_id}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to create revisit task for channel {channel.channel_id}: {str(e)}"
                        )
        except Exception as e:
            logger.error(f"Error processing due channels: {str(e)}")
            raise
