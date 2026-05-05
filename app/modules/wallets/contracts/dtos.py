from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.common.enums.wallet_enums import WalletTypesEnum


class FullWalletInfoDTO(BaseModel):
    """DTO схема для передачи полных данных кошельков"""

    wallet_id: UUID
    address: str
    pin_hash: str
    is_blocked: bool
    wallet_type: WalletTypesEnum
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class SecurityWalletInfoDTO(BaseModel):
    """DTO схема для передачи безопасных данных кошельков"""

    address: str
    wallet_type: WalletTypesEnum

    model_config = ConfigDict(from_attributes=True)