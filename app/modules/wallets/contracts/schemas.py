from pydantic import BaseModel, Field, ConfigDict


class CreateWalletSchema(BaseModel):
    """Схема для создания кошельков"""

    pin: str


class UpdateWalletSchema(BaseModel):
    """Схема для ввода данных при обновлении информации"""

    address: str
    pin: str


class UpdateParamsWalletSchema(BaseModel):
    """Схема для обновления информации кошельков"""

    pin: str | None = Field(default=None, examples=[None])

    model_config = ConfigDict(extra='forbid')


class CloseWalletSchema(BaseModel):
    """Схема для закрытия кошельков"""

    address: str
    pin: str
