# main.py
import asyncio
import multiprocessing
import signal
import sys
from typing import Optional

import dramatiq
import uvicorn
from fastapi import FastAPI
from dramatiq.brokers.stub import StubBroker
from dramatiq.worker import Worker

from tasks.application.tasks_service import TasksService
from tasks.infrastructure.repositories.tasks_repository import TasksRepository
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI()
tasks_repository = TasksRepository()
tasks_service = TasksService(repository=tasks_repository)

# Global worker reference for cleanup
worker: Optional[Worker] = None

async def start_dramatiq_worker():
    """Start Dramatiq worker in the same process"""
    global worker
    
    # Get the broker instance that was set up in tasks_queue.py
    broker = dramatiq.get_broker()
    
    # Create and start the worker
    worker = Worker(broker, worker_timeout=1000)
    worker.start()
    
    logger.info("Dramatiq worker started successfully")

async def cleanup_worker():
    """Cleanup worker on shutdown"""
    global worker
    if worker:
        logger.info("Stopping Dramatiq worker...")
        worker.stop()
        logger.info("Dramatiq worker stopped successfully")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await tasks_service.start()
    await start_dramatiq_worker()
    logger.info("All services started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    tasks_service.stop()
    await cleanup_worker()
    logger.info("All services stopped successfully")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}")
    asyncio.create_task(shutdown_event())
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the FastAPI application with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=1  # Single worker since we're running Dramatiq in the same process
    )