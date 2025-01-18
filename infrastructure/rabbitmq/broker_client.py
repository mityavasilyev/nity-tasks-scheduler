import subprocess
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import CurrentMessage
import requests
from requests.auth import HTTPBasicAuth

from config import settings
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


class BrokerClient:
    _instance = None
    _broker = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrokerClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._broker is None:
            self._ensure_vhost_exists()
            self._initialize_broker()
            logger.info("RabbitMQ broker initialized successfully")


    def _ensure_vhost_exists(self):
        """Ensure that the virtual host exists, create if it doesn't"""
        try:
            # First try HTTP API
            self._create_vhost_via_api()
        except Exception as api_error:
            logger.warning(f"Failed to create vhost via HTTP API: {str(api_error)}")
            try:
                # Fallback to rabbitmqctl command
                self._create_vhost_via_command()
            except Exception as cmd_error:
                logger.error(f"Failed to create vhost via command: {str(cmd_error)}")
                raise

    def _create_vhost_via_api(self):
        """Create virtual host using RabbitMQ HTTP API"""
        api_url = f"http://{settings.RABBITMQ_HOST}:{settings.RABBITMQ_UTILITY_PORT}/api/vhosts/{settings.RABBITMQ_VHOST}"

        # Check if vhost exists
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        )

        if response.status_code == 404:
            logger.info(f"Virtual host '{settings.RABBITMQ_VHOST}' not found, creating...")
            # Create vhost if it doesn't exist
            response = requests.put(
                api_url,
                auth=HTTPBasicAuth(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
            )
            response.raise_for_status()

            # Set permissions for the user on the new vhost
            permissions_url = f"http://{settings.RABBITMQ_HOST}:{settings.RABBITMQ_UTILITY_PORT}/api/permissions/{settings.RABBITMQ_VHOST}/{settings.RABBITMQ_USER}"
            permissions_data = {
                "configure": ".*",
                "write": ".*",
                "read": ".*"
            }
            response = requests.put(
                permissions_url,
                json=permissions_data,
                auth=HTTPBasicAuth(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
            )
            response.raise_for_status()

            logger.info(f"Created virtual host '{settings.RABBITMQ_VHOST}' via HTTP API")
        elif response.status_code == 200:
            logger.info(f"Virtual host '{settings.RABBITMQ_VHOST}' already exists")
        else:
            response.raise_for_status()

    def _create_vhost_via_command(self):
        """Create virtual host using rabbitmqctl command"""
        # Create vhost
        subprocess.run(
            ["rabbitmqctl", "add_vhost", settings.RABBITMQ_VHOST],
            check=True,
            capture_output=True
        )

        # Set permissions
        subprocess.run([
            "rabbitmqctl", "set_permissions",
            "-p", settings.RABBITMQ_VHOST,
            settings.RABBITMQ_USER,
            ".*", ".*", ".*"
        ], check=True, capture_output=True)

        logger.info(f"Created virtual host '{settings.RABBITMQ_VHOST}' via rabbitmqctl")

    def _initialize_broker(self):
        """Initialize RabbitMQ broker with dramatiq"""
        try:
            url = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@" \
                  f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/{settings.RABBITMQ_VHOST}"

            self._broker = RabbitmqBroker(url=url)
            dramatiq.set_broker(self._broker)

            # Add CurrentMessage middleware if not already present
            if not any(isinstance(m, CurrentMessage) for m in self._broker.middleware):
                self._broker.add_middleware(CurrentMessage())

            logger.info("RabbitMQ broker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RabbitMQ broker: {str(e)}")
            raise

    @property
    def broker(self) -> RabbitmqBroker:
        """Get the initialized broker instance"""
        return self._broker

    def shutdown(self):
        """Cleanup method to properly close broker connections"""
        try:
            if self._broker:
                self._broker.close()
                logger.info("RabbitMQ broker connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing broker connection: {str(e)}")