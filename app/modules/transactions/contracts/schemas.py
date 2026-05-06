from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class CreateDepositTrnSchema(BaseModel):
    """Схема для создания транзакции пополнения"""

    from_wallet_id: UUID
    to_wallet_id: UUID
    amount: Decimal
    fee: Decimal
    from_currency: str


class CreateWithdrawTrnSchema(BaseModel):
    """Схема для создания транзакции снятия"""

    from_wallet_id: UUID
    to_wallet_id: UUID
    amount: Decimal
    fee: Decimal
    from_currency: str


class CreateExchangeTrnSchema(BaseModel):
    """Схема для создания транзакции обмена"""

    from_wallet_id: UUID
    to_wallet_id: UUID
    amount: Decimal
    fee: Decimal
    rate: Decimal
    from_currency: str
    to_currency: str
