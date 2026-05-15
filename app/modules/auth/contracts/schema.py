from pydantic import BaseModel, EmailStr


class LoginUserSchema(BaseModel):
    """Схема для входа в аккаунт пользователя"""

    email: EmailStr
    password: str


class RefreshTokensSchema(BaseModel):
    """Схема для обновления токенов"""

    refresh_token: str
