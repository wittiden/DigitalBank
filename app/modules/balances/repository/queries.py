from typing import TYPE_CHECKING
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import BalanceModel

if TYPE_CHECKING:
    from app.database.models import WalletModel


class BalanceQueriesRepository:
    """Репозиторий для управления select запросами для балансов в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_balance_by_id(self, balance_id: UUID) -> 'BalanceModel | None':
        return await self._async_session.get(BalanceModel, balance_id)

    async def select_balances(self, offset: int = 0, limit: int = 100) -> list['BalanceModel']:
        objs = await self._async_session.execute(select(BalanceModel).offset(offset).limit(limit))
        return list(objs.scalars().all())

    async def select_balances_by_wallet_id(self, wallet_id: UUID) -> list['BalanceModel']:
        objs = await self._async_session.execute(select(BalanceModel).where(BalanceModel.wallet_id == wallet_id))
        return list(objs.scalars().all())

    async def select_balances_by_wallet(self, wallet: 'WalletModel') -> list['BalanceModel']:
        objs = await self._async_session.execute(select(BalanceModel).where(BalanceModel.wallet_id == wallet.wallet_id))
        return list(objs.scalars().all())

    async def select_balances_count(self, wallet_id: UUID) -> int:
        objs = await self._async_session.execute(select(func.count(BalanceModel.balance_id)).where(BalanceModel.wallet_id == wallet_id))
        return objs.scalar()
