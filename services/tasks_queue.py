import asyncio
from typing import Union

import dramatiq

from config import settings
from domain.models import TaskType
from infrastructure.di.container import get_worker_container
from infrastructure.nity.channel_intelligence_client import ChannelIntelligenceClient
from infrastructure.rabbitmq.broker_client import BrokerClient
from services.tasks_worker import TaskExecutionMiddleware
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)

# Initialize broker with middleware
container = get_worker_container()
broker_client = container.get(BrokerClient)
middleware = container.get(TaskExecutionMiddleware)
broker_client.broker.add_middleware(middleware=middleware)
# Set broker as default for dramatiq
dramatiq.set_broker(broker_client.broker)

client = container.get(ChannelIntelligenceClient)


async def _start_tracking_channel_async(channel_id: str):
    """Async implementation of channel tracking"""

    async with client.connection():
        success, message = await client.start_tracking_new_channel(channel_id=int(channel_id))
        logger.info(f"Start tracking result: Success={success}, Message={message}")
        return success, message


async def _revisit_channel_async(channel_id: str):
    """Async implementation of channel revisiting"""
    async with client.connection():
        success, message = await client.revisit_channel(channel_id=int(channel_id))
        logger.info(f"Revisit result: Success={success}, Message={message}")
        return success, message


@dramatiq.actor(queue_name=settings.RABBITMQ_CHANNEL_TASKS_QUEUE)
def start_tracking_channel(channel_id: Union[str, int]):
    """
    Start tracking a new channel.
    This will be executed when a new channel needs to be added to tracking.
    """
    # Convert channel_id to string if it's an integer
    channel_id_str = str(channel_id)
    logger.info(f"Starting to track channel: {channel_id_str}")

    try:
        # Run the async function in the event loop
        success, message = asyncio.run(_start_tracking_channel_async(channel_id_str))

        if not success:
            logger.error(f"Failed to start tracking channel {channel_id_str}: {message}")
            raise RuntimeError(f"Failed to start tracking: {message}")

        logger.info(f"Successfully started tracking channel: {channel_id_str}")
        return
    except Exception as e:
        logger.error(f"Error in start_tracking_channel: {str(e)}")
        raise


@dramatiq.actor(queue_name=settings.RABBITMQ_CHANNEL_TASKS_QUEUE)
def revisit_channel(channel_id: Union[str, int]):
    """
    Revisit an existing channel to update its data.
    This will be executed periodically for channels we're already tracking.
    """
    # Convert channel_id to string if it's an integer
    channel_id_str = str(channel_id)
    logger.info(f"Revisiting channel: {channel_id_str}")

    try:
        # Run the async function in the event loop
        success, message = asyncio.run(_revisit_channel_async(channel_id_str))

        if not success:
            logger.error(f"Failed to revisit channel {channel_id_str}: {message}")
            raise RuntimeError(f"Failed to revisit: {message}")

        logger.info(f"Successfully revisited channel: {channel_id_str}")
        return
    except Exception as e:
        logger.error(f"Error in revisit_channel: {str(e)}")
        raise


def enqueue_task(task_type: TaskType, channel_id: Union[str, int]) -> str:
    """
    Enqueue a task based on its type and return the message ID.
    Channel ID can be either string or integer.
    """
    actor = {
        TaskType.START_TRACKING: start_tracking_channel,
        TaskType.REVISIT_CHANNEL: revisit_channel,
    }[task_type]

    message = actor.send(str(channel_id))
    return message.message_id


def ping() -> None:
    return None
