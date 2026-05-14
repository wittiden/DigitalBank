from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DepositDraftResponse(BaseModel):
    """Схема для ответа с данными чека транзакции пополнения"""

    from_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str

    model_config = ConfigDict(from_attributes=True)


class WithdrawDraftResponse(BaseModel):
    """Схема для ответа с данными чека транзакции снятия"""

    from_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str

    model_config = ConfigDict(from_attributes=True)


class TransferDraftResponse(BaseModel):
    """Схема для ответа с данными чека транзакции перевода"""

    from_address: str
    to_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str

    model_config = ConfigDict(from_attributes=True)


class ExchangeDraftResponse(BaseModel):
    """Схема для ответа с данными чека транзакции обмена"""

    from_address: str
    to_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str

    model_config = ConfigDict(from_attributes=True)
