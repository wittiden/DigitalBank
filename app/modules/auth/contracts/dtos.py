from pydantic import BaseModel, ConfigDict


class TokenInfoDTO(BaseModel):
    """DTO схема для передачи информации о токене"""

    token: str
    token_type: str = 'Bearer'

    model_config = ConfigDict(from_attributes=True)
