from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.common.enums.balance_enums import BalanceTypesEnum


class FullBalanceInfoResponse(BaseModel):
    """Схема для ответа с полными данными баланса"""

    balance_id: UUID
    currency: str
    amount: Decimal
    is_frozen: bool
    balance_type: BalanceTypesEnum
    wallet_id: UUID

    model_config = ConfigDict(from_attributes=True)


class SecurityBalanceInfoResponse(BaseModel):
    """Схема для ответа с безопасными данными баланса"""

    currency: str
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)
