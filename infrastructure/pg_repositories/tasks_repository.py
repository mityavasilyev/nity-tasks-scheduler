from typing import Optional, List

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, BigInteger
from sqlalchemy.orm import Session

from domain.models import TaskStatus, TaskType, Task as TaskModel
from infrastructure.pg_repositories.engine import Base, engine
from utils.logger import AppLogger
from utils.time_utils import TimeUtils

logger = AppLogger.get_logger(__name__)


class TaskEntity(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    message_id = Column(String, unique=True, nullable=False)  # Dramatiq message ID
    task_type = Column(SQLEnum(TaskType), nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=TimeUtils.current_datetime())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    user_id_to_notify = Column(BigInteger, nullable=True)


class TasksRepository:
    def __init__(self):
        Base.metadata.create_all(engine)

    def create_task(self, session: Session, message_id: str, task_type: TaskType, channel_id: int,
                    user_id_to_notify: Optional[int] = None) -> TaskModel:
        """Create a new task record"""
        try:
            task_entity = TaskEntity(
                message_id=message_id,
                task_type=task_type,
                channel_id=channel_id,
                status=TaskStatus.PENDING,
                user_id_to_notify=user_id_to_notify
            )
            session.add(task_entity)
            session.commit()
            session.refresh(task_entity)
            return TaskModel.model_validate(task_entity)
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create task: {str(e)}")
            raise

    def update_task_status(
            self,
            session: Session,
            message_id: str,
            status: TaskStatus,
            error_message: Optional[str] = None
    ) -> Optional[TaskModel]:
        """Update task status and related fields"""
        try:
            task_entity = session.query(TaskEntity).filter_by(message_id=message_id).first()
            if task_entity:
                task_entity.status = status
                if status == TaskStatus.RUNNING:
                    task_entity.started_at = TimeUtils.current_datetime()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task_entity.completed_at = TimeUtils.current_datetime()
                if error_message:
                    task_entity.error_message = error_message
                session.commit()
                session.refresh(task_entity)
                return TaskModel.model_validate(task_entity)
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update task status: {str(e)}")
            raise

    def get_task_by_message_id(self, session: Session, message_id: str) -> Optional[TaskModel]:
        """Get task by Dramatiq message ID"""
        task_entity = session.query(TaskEntity).filter_by(message_id=message_id).first()
        return TaskModel.model_validate(task_entity) if task_entity else None

    def get_tasks_by_status(self, session: Session, status: TaskStatus) -> List[TaskModel]:
        """Get all tasks with specified status"""
        task_entities = session.query(TaskEntity).filter_by(status=status).all()
        return [TaskModel.model_validate(entity) for entity in task_entities]

    def get_task_by_status(self, channel_id: int, session: Session, task_type: TaskType, status: TaskStatus) -> \
    Optional[TaskModel]:
        """Get all tasks with specified status"""
        entity = (session.query(TaskEntity)
                  .filter_by(channel_id=channel_id)
                  .filter_by(task_type=task_type)
                  .filter_by(status=status).first())
        return TaskModel.model_validate(entity) if entity else None

    def get_all_tasks(self, session: Session) -> List[TaskModel]:
        """Get all tasks"""
        task_entities = session.query(TaskEntity).all()
        return [TaskModel.model_validate(entity) for entity in task_entities]

    def get_task_by_id(self, session: Session, task_id: int) -> Optional[TaskModel]:
        """Get task by ID"""
        task_entity = session.query(TaskEntity).filter_by(id=task_id).first()
        return TaskModel.model_validate(task_entity) if task_entity else None

    def update_task_message_id(self, session: Session, task_id: int, message_id: str) -> TaskModel:
        """Update task's message ID"""
        try:
            task_entity = session.query(TaskEntity).filter_by(id=task_id).first()
            if task_entity:
                task_entity.message_id = message_id
                session.commit()
                session.refresh(task_entity)
                return TaskModel.model_validate(task_entity)
            raise ValueError(f"Task with ID {task_id} not found")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update task message ID: {str(e)}")
            raise

    def get_tasks_by_channel(self, session: Session, channel_id: int) -> List[TaskModel]:
        """Get all tasks for a specific channel"""
        task_entities = session.query(TaskEntity).filter_by(channel_id=channel_id).all()
        return [TaskModel.model_validate(entity) for entity in task_entities]
