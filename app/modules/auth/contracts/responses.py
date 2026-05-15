from pydantic import BaseModel, ConfigDict


class TokenInfoResponse(BaseModel):
    """Схема для ответа с информацией о токене"""

    access_token: str
    refresh_token: str
    token_type: str

    model_config = ConfigDict(from_attributes=True)
