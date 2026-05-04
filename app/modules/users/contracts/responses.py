from uuid import UUID
from pydantic import BaseModel

from app.common.enums.user_enums import UserStatusesEnum


class FullUserInfoResponse(BaseModel):
    """DTO схема для передачи полных данных пользователя"""

    user_id: UUID
    name: str
    email: str
    password_hash: str
    is_blocked: bool
    user_status: UserStatusesEnum