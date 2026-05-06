from typing import Any
from uuid import UUID
from pydantic import BaseModel, EmailStr


class CreateWalletSchema(BaseModel):
    """Схема для создания кошельков"""

    pin: str
    email: EmailStr
    password: str


class UpdateWalletSchema(BaseModel):
    """Схема для обновления информации кошельков"""

    address: str
    pin: str
    data: dict[str, Any]


class UpdateWalletUserSchema(BaseModel):
    """Схема для обновления владельца кошелька"""

    address: str
    pin: str
    email: EmailStr
    password: str


class CloseWalletSchema(BaseModel):
    """Схема для закрытия кошельков"""

    address: str
    pin: str


class ShowMyWalletsSchema(BaseModel):
    """Схема для поиска собственных кошельков"""

    email: EmailStr
    password: str

