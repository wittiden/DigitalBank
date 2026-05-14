from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.common.enums.transaction_enums import TransactionStatusesEnum, TransactionTypesEnum


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

    model_config = ConfigDict(from_attributes=True)
