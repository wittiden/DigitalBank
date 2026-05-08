from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel

from app.common.enums.transaction_enums import TransactionTypesEnum, TransactionStatusesEnum


class FullTrnInfoResponse(BaseModel):
    """Схема для ответа с полными данными транзакции"""

    transaction_id: UUID
    from_address: str
    to_address: str
    amount: Decimal
    fee: Decimal
    rate: Decimal | None
    started_at: datetime
    completed_at: datetime | None
    from_currency: str
    to_currency: str | None
    transaction_type: TransactionTypesEnum
    transaction_status: TransactionStatusesEnum


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
