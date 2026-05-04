from pydantic import BaseModel, EmailStr


class CreateUserSchema(BaseModel):
    """Схема создания пользователя"""

    name: str
    email: EmailStr
    password: str

