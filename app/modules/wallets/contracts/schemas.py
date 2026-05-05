from typing import Any

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


class CloseWalletSchema(BaseModel):
    """Схема для закрытия кошельков"""

    address: str
    pin: str


class ShowWalletByAddressSchema(BaseModel):
    """Схема для поиска кошелька по адресу"""

    address: str
    pin: str
