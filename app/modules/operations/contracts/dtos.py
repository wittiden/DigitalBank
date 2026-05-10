from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class DepositDraftDTO(BaseModel):
    """DTO схема для передачи черновика с данными о транзакции пополнения"""

    from_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str

    model_config = ConfigDict(from_attributes=True)


class WithdrawDraftDTO(BaseModel):
    """DTO схема для передачи черновика с данными о транзакции снятия"""

    from_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str

    model_config = ConfigDict(from_attributes=True)


class TransferDraftDTO(BaseModel):
    """DTO схема для передачи черновика с данными о транзакции перевода"""

    from_address: str
    to_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str

    model_config = ConfigDict(from_attributes=True)


class ExchangeDraftDTO(BaseModel):
    """DTO схема для передачи черновика с данными о транзакции перевода"""

    from_address: str
    to_address: str
    amount: Decimal
    fee: Decimal
    from_currency: str

    model_config = ConfigDict(from_attributes=True)
