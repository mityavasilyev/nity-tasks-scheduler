from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    START_TRACKING = "start_tracking"
    REVISIT_CHANNEL = "revisit_channel"


class TaskBase(BaseModel):
    channel_id: int
    task_type: TaskType


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message_id: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class TrackedChannel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_id: int
    revisiting: bool
    last_revisited: Optional[datetime] = None
    created_at: datetime
