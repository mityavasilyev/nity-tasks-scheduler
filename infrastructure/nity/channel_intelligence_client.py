from dataclasses import dataclass
from typing import Tuple

from infrastructure.nity.base import GrpcClientConfig, BaseGrpcClient
from infrastructure.nity.proto.channel_intelligence import ChannelIntelligenceStub
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


@dataclass
class ChannelIntelligenceConfig(GrpcClientConfig):
    pass


class ChannelIntelligenceClient(BaseGrpcClient[ChannelIntelligenceStub]):

    @property
    def stub_class(self) -> type[ChannelIntelligenceStub]:
        return ChannelIntelligenceStub

    async def start_tracking_new_channel(self, channel_id: int) -> Tuple[bool, str]:
        try:
            response = await self.stub.start_tracking_new_channel(channel_id=channel_id)
            if not response.success:
                raise ValueError(f"Failed to start tracking channel {channel_id}: {response.message}")
            return response.success, response.message
        except Exception as e:
            logger.error(f"Error in start_tracking_new_channel: {str(e)}")
            raise

    async def revisit_channel(self, channel_id: int) -> Tuple[bool, str]:
        try:
            response = await self.stub.revisit_channel(channel_id=channel_id)
            if not response.success:
                raise ValueError(f"Failed to revisit channel {channel_id}: {response.message}")
            return response.success, response.message
        except Exception as e:
            logger.error(f"Error in revisit_channel: {str(e)}")
            raise
