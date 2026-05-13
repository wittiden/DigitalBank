from decimal import Decimal

from pydantic import BaseModel


class DepositSchema(BaseModel):
    """Схема для создания транзакции пополнения"""

    address: str
    pin: str
    amount: Decimal
    currency: str


class WithdrawSchema(BaseModel):
    """Схема для создания транзакции снятия"""

    address: str
    pin: str
    amount: Decimal
    currency: str


class TransferSchema(BaseModel):
    """Схема для создания транзакции пополнения"""

    from_address: str
    pin: str
    to_address: str
    amount: Decimal
    currency: str


class ExchangeSchema(BaseModel):
    """Схема для создания транзакции обмена"""

    from_address: str
    pin: str
    to_address: str
    amount: Decimal
    from_currency: str
    to_currency: str
