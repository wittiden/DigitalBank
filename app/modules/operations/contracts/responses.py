from decimal import Decimal

from pydantic import BaseModel


class DepositDraftResponse(BaseModel):
    """Схема для ответа с данными чека транзакции пополнения"""

    from_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str


class WithdrawDraftResponse(BaseModel):
    """Схема для ответа с данными чека транзакции снятия"""

    from_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str


class TransferDraftResponse(BaseModel):
    """Схема для ответа с данными чека транзакции перевода"""

    from_address: str
    to_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str


class ExchangeDraftResponse(BaseModel):
    """Схема для ответа с данными чека транзакции обмена"""

    from_address: str
    to_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str
