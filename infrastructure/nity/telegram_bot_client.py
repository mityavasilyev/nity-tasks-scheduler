from dataclasses import dataclass

from infrastructure.nity.base import GrpcClientConfig, BaseGrpcClient
from infrastructure.nity.proto.user_interactions import TelegramBotServiceStub, NotifyUserResponse
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


@dataclass
class TelegramBotClientConfig(GrpcClientConfig):
    pass


class TelegramBotClient(BaseGrpcClient):

    @property
    def stub_class(self) -> type[TelegramBotServiceStub]:
        return TelegramBotServiceStub

    async def notify_nity_user(self, nity_user_id: int, message: str) -> bool:
        try:
            response: NotifyUserResponse = await self.stub.notify_user(
                user_id=nity_user_id,
                message=message
            )
            return response.success
        except Exception as e:
            logger.error(f"Error in notify_user: {str(e)}")
            raise
