from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.common.enums.balance_enums import BalanceTypesEnum


class FullBalanceInfoDTO(BaseModel):
    """DTO схема для передачи полных данных баланса"""

    balance_id: UUID
    currency: str
    amount: Decimal
    is_frozen: bool
    balance_type: BalanceTypesEnum
    wallet_id: UUID

    model_config = ConfigDict(from_attributes=True)


class SecurityBalanceInfoDTO(BaseModel):
    """DTO схема для передачи безопасных данных баланса"""

    currency: str
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)
