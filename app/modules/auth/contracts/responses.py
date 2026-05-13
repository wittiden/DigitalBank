from pydantic import BaseModel


class TokenInfoResponse(BaseModel):
    """Схема для ответа с информацией о токене"""

    token: str
    token_type: str
