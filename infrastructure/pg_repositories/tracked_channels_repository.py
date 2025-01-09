from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, Boolean, DateTime, BigInteger, select, update
from sqlalchemy.orm import Session

from infrastructure.pg_repositories.engine import Base, engine
from domain.models import TrackedChannel
from utils.logger import AppLogger
from utils.time_utils import TimeUtils

logger = AppLogger.get_logger(__name__)


class TrackedChannelEntity(Base):
    __tablename__ = 'tracked_channels'

    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False, unique=True)
    revisiting = Column(Boolean, nullable=False, default=True)
    last_revisited = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=TimeUtils.current_datetime())


class TrackedChannelsRepository:
    def __init__(self, session: Session):
        self._session = session
        Base.metadata.create_all(engine)

    def add_channel(self, channel_id: int) -> TrackedChannel:
        """Add a new channel to tracking"""
        try:
            channel_entity = TrackedChannelEntity(
                channel_id=channel_id,
                revisiting=True,
                last_revisited=TimeUtils.current_datetime(),
                created_at=TimeUtils.current_datetime()
            )
            self._session.add(channel_entity)
            self._session.commit()
            self._session.refresh(channel_entity)
            return TrackedChannel.model_validate(channel_entity)
        except Exception as e:
            self._session.rollback()
            logger.error(f"Failed to add channel: {str(e)}")
            raise

    def update_last_revisited(self, channel_id: int) -> Optional[TrackedChannel]:
        """Update last_revisited timestamp for a channel"""
        try:
            stmt = update(TrackedChannelEntity).where(
                TrackedChannelEntity.channel_id == channel_id
            ).values(
                last_revisited=TimeUtils.current_datetime()
            ).returning(TrackedChannelEntity)

            result = self._session.execute(stmt)
            self._session.commit()
            updated = result.scalar_one_or_none()
            return TrackedChannel.model_validate(updated) if updated else None
        except Exception as e:
            self._session.rollback()
            logger.error(f"Failed to update last_revisited: {str(e)}")
            raise

    def get_channels_due_revisit(self, interval_minutes: int) -> List[TrackedChannel]:
        """Get all channels that haven't been revisited in the specified interval"""
        cutoff_time = TimeUtils.current_datetime().timestamp() - (interval_minutes * 60)
        stmt = select(TrackedChannelEntity).where(
            TrackedChannelEntity.revisiting == True,
            (
                TrackedChannelEntity.last_revisited.is_(None) |
                (TrackedChannelEntity.last_revisited <= datetime.fromtimestamp(cutoff_time))
            )
        )
        result = self._session.execute(stmt)
        channels = result.scalars().all()
        return [TrackedChannel.model_validate(ch) for ch in channels]

    def set_revisiting(self, channel_id: int, revisiting: bool) -> Optional[TrackedChannel]:
        """Enable or disable revisiting for a channel"""
        try:
            stmt = update(TrackedChannelEntity).where(
                TrackedChannelEntity.channel_id == channel_id
            ).values(
                revisiting=revisiting
            ).returning(TrackedChannelEntity)

            result = self._session.execute(stmt)
            self._session.commit()
            updated = result.scalar_one_or_none()
            return TrackedChannel.model_validate(updated) if updated else None
        except Exception as e:
            self._session.rollback()
            logger.error(f"Failed to update revisiting status: {str(e)}")
            raise

    def get_channel(self, channel_id: int) -> Optional[TrackedChannel]:
        """Get channel by ID"""
        channel = self._session.query(TrackedChannelEntity).filter_by(channel_id=channel_id).first()
        return TrackedChannel.model_validate(channel) if channel else None