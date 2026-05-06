from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel

from app.common.enums.transaction_enums import TransactionTypesEnum, TransactionStatusesEnum


class FullTrnInfoResponse(BaseModel):
    """Схема для ответа с полными данными транзакции"""

    transaction_id: UUID
    from_wallet_id: UUID
    to_wallet_id: UUID
    amount: Decimal
    fee: Decimal
    rate: Decimal | None
    started_at: datetime
    completed_at: datetime | None
    from_currency: str
    to_currency: str | None
    transaction_type: TransactionTypesEnum
    transaction_status: TransactionStatusesEnum
