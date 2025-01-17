import logging
import sys

from dramatiq.cli import main as dramatiq_main

from config import settings
from services import tasks_queue
from services.tasks_health import SimpleHealthCheck
from utils.logger import AppLogger

# Configure logging
AppLogger.setup(log_file='worker.log', level=logging.DEBUG)
logger = AppLogger.get_logger(__name__)


def run_worker():
    """Run the dramatiq worker"""
    try:
        logger.info("Starting worker process")
        tasks_queue.ping()

        sys.argv = [
            "dramatiq",
            "--processes", str(settings.WORKER_PROCESSES),
            "--threads", str(settings.WORKER_THREADS),
            "services.tasks_queue"
        ]
        dramatiq_main()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker error: {str(e)}")
        raise


if __name__ == "__main__":
    healthcheck = SimpleHealthCheck(80)
    run_worker()
