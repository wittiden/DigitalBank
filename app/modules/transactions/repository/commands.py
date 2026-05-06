from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums.transaction_enums import TransactionStatusesEnum
from app.common.enums.transaction_enums import TransactionTypesEnum
from app.database.models import TransactionModel
from app.modules.transactions.exceptions import InvalidFieldError


class TrnCommandsRepository:
    """Репозиторий для управления create, update, delete запросами для транзакций в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_trn_info(self, from_wallet_id: UUID, amount: Decimal, fee: Decimal, started_at: datetime, from_currency: str, transaction_type: 'TransactionTypesEnum', to_wallet_id: UUID, rate: Decimal = None, completed_at: datetime = None, to_currency: str = None) -> 'TransactionModel':
        trn = TransactionModel(from_wallet_id=from_wallet_id, to_wallet_id=to_wallet_id, amount=amount, fee=fee, rate=rate, started_at=started_at, completed_at=completed_at, from_currency=from_currency, to_currency=to_currency, transaction_status=TransactionStatusesEnum.UNKNOWN, transaction_type=transaction_type)

        self._async_session.add(trn)
        await self._async_session.flush()

        return trn

    async def partial_update_trn(self, trn: 'TransactionModel', data: dict[str, Any]) -> 'TransactionModel':
        for key, value in data.items():
            if not hasattr(trn, key):
                raise InvalidFieldError('Invalid field error')

            setattr(trn,key, value)

        await self._async_session.flush()

        return trn
