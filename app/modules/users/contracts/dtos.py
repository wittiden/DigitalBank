from pydantic import BaseModel, ConfigDict
from uuid import UUID

from app.common.enums.user_enums import UserStatusesEnum


class FullUserInfoDTO(BaseModel):
    """DTO схема для передачи полных данных пользователя"""

    user_id: UUID
    name: str
    email: str
    password_hash: str
    is_blocked: bool
    user_status: UserStatusesEnum

    model_config = ConfigDict(from_attributes=True)