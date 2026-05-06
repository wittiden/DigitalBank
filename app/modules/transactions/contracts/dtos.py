from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from app.common.enums.transaction_enums import TransactionTypesEnum, TransactionStatusesEnum


class FullTrnInfoDTO(BaseModel):
    """DTO схема для передачи полных данных о транзакции"""

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

    model_config = ConfigDict(from_attributes=True)
