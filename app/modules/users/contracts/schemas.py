from typing import Any
from pydantic import BaseModel, EmailStr


class CreateUserSchema(BaseModel):
    """Схема создания пользователя"""

    name: str
    email: EmailStr
    password: str


class UpdateUserSchema(BaseModel):
    """Схема обновления данных пользователя"""

    email: EmailStr
    password: str
    data: dict[str, Any]