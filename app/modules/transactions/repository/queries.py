from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import TransactionModel


class TrnQueriesRepository:
    """Репозиторий для управления select запросами для транзакций в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_trn_by_id(self, trn_id: UUID) -> 'TransactionModel | None':
        return await self._async_session.get(TransactionModel, trn_id)

    async def select_trns(self, offset: int = 0, limit: int = 100) -> list['TransactionModel']:
        objs = await self._async_session.execute(select(TransactionModel).offset(offset).limit(limit))
        return list(objs.scalars().all())