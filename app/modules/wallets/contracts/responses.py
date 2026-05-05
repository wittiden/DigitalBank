from uuid import UUID
from pydantic import BaseModel

from app.common.enums.wallet_enums import WalletTypesEnum


class FullWalletInfoResponse(BaseModel):
    """Схема для ответа с полными данными кошелька"""

    wallet_id: UUID
    address: str
    pin_hash: str
    is_blocked: bool
    wallet_type: WalletTypesEnum
    user_id: UUID


class SecurityWalletInfoResponse(BaseModel):
    """Схема для ответа с безопасными данными кошелька"""

    address: str
    wallet_type: WalletTypesEnum
