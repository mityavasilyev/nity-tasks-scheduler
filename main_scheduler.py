import asyncio
import logging

from api.server import TasksGrpcServer
from infrastructure.di.container import get_container
from services.revisit_scheduler import RevisitScheduler
from utils.healthcheck import run_health_server
from utils.logger import AppLogger

AppLogger.setup(log_file='assistant.log', level=logging.INFO)
logger = AppLogger.get_logger(__name__)


async def main():
    """Initialize services on startup"""
    await run_health_server()
    container = get_container()
    logger.info("All services started successfully")
    server = container.get(TasksGrpcServer)
    revisit_scheduler = container.get(RevisitScheduler)
    asyncio.create_task(revisit_scheduler.start())
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
