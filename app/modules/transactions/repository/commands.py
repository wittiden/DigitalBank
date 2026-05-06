from datetime import datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums.transaction_enums import TransactionStatusesEnum
from app.common.enums.transaction_enums import TransactionTypesEnum
from app.database.models import TransactionModel


class TrnCommandsRepository:
    """Репозиторий для управления create, update, delete запросами для транзакций в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_trn_info(self, from_wallet_id: UUID, amount: Decimal, fee: Decimal, started_at: datetime, completed_at: datetime, transaction_type: 'TransactionTypesEnum', to_wallet_id: UUID = None, rate: Decimal = None, from_currency: str = None, to_currency: str = None) -> 'TransactionModel':
        trn = TransactionModel(from_wallet_id=from_wallet_id, to_wallet_id=to_wallet_id, amount=amount, fee=fee, rate=rate, started_at=started_at, completed_at=completed_at, from_currency=from_currency, to_currency=to_currency, transaction_status=TransactionStatusesEnum.UNKNOWN, transaction_type=transaction_type)

        self._async_session.add(trn)
        await self._async_session.flush()

        return trn

    async def partial_update_trn_status(self, trn: 'TransactionModel', new_trn_status: TransactionStatusesEnum) -> 'TransactionModel':
        setattr(trn, 'transaction_status', new_trn_status)
        await self._async_session.flush()

        return trn
