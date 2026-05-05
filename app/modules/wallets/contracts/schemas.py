from pydantic import BaseModel, EmailStr


class CreateWalletSchema(BaseModel):
    """Схема для создания кошельков"""

    pin: str
    email: EmailStr
    password: str