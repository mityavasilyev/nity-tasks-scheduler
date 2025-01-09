import logging
import sys
from pathlib import Path


class AppLogger:
    """Simple application-wide logging utility."""

    _initialized: bool = False

    @classmethod
    def setup(cls, log_file: str = 'app.log', level: int = logging.INFO) -> None:
        """
        Initialize logging configuration.
        Should be called once at application startup.

        Args:
            log_file: Name of the log file
            level: Logging level (default: INFO)
        """
        if cls._initialized:
            return

        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_dir / log_file)
            ]
        )

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance for the specified name.

        Args:
            name: Logger name (typically __name__ of the calling module)

        Returns:
            Configured logger instance
        """
        if not cls._initialized:
            cls.setup()
        return logging.getLogger(name)
