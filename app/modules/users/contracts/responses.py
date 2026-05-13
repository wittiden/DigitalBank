from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.common.enums.user_enums import UserStatusesEnum


class FullUserInfoResponse(BaseModel):
    """Схема для ответа с полными данными пользователя"""

    user_id: UUID
    name: str
    email: EmailStr
    is_blocked: bool
    user_status: UserStatusesEnum


class SecurityUserInfoResponse(BaseModel):
    """Схема для ответа с безопасными данными пользователя"""

    name: str
    email: EmailStr
