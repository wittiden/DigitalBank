from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CreateUserSchema(BaseModel):
    """Схема создания пользователя"""

    name: str
    email: EmailStr
    password: str


class UpdateUserSchema(BaseModel):
    """Схема обновления данных пользователя"""

    name: str | None = Field(default=None, examples=[None])
    email: EmailStr | None = Field(default=None, examples=[None])
    password: str | None = Field(default=None, examples=[None])

    model_config = ConfigDict(extra='forbid')
