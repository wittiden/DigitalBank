from pydantic import BaseModel, EmailStr


class LoginUserSchema(BaseModel):
    """Схема с данными для входа в аккаунт"""

    email: EmailStr
    password: str
