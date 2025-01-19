from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/tasks"

    # Channel Intelligence gRPC settings
    CHANNEL_INTELLIGENCE_GRPC_HOST: str = "localhost"
    CHANNEL_INTELLIGENCE_GRPC_PORT: int = 50052

    # RabbitMQ settings
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_UTILITY_PORT: int = 15672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "collector"
    RABBITMQ_CHANNEL_TASKS_QUEUE: str = "channel_tasks.DQ"

    # Worker settings
    WORKER_PROCESSES: int = 1
    WORKER_THREADS: int = 1

    # Channel revisit settings
    REVISIT_INTERVAL_MINUTES: int = 360  # 6 hours
    REVISIT_CHECK_INTERVAL_SECONDS: int = 60  # How often to check for due channels

    # gRPC Server Configuration
    GRPC_SERVER_PORT: int = 50051

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
