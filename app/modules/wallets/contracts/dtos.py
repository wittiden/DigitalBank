from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.common.enums.wallet_enums import WalletTypesEnum


class FullWalletInfoDTO(BaseModel):
    """DTO схема для передачи полных данных кошельков"""

    wallet_id: UUID
    address: UUID
    pin_hash: str
    is_blocked: bool
    wallet_type: WalletTypesEnum
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)

