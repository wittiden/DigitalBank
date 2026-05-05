from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import UserModel
from app.database.models import WalletModel


class WalletQueriesRepository:
    """Репозиторий для управления select запросами для кошельков в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_wallet_by_id(self, wallet_id: UUID) -> 'WalletModel | None':
        return await self._async_session.get(WalletModel, wallet_id)

    async def select_wallets_by_user(self, user: 'UserModel', offset: int = 0, limit: int = 100) -> list['WalletModel']:
        objs  = await self._async_session.execute(select(WalletModel).where(WalletModel.user_id == user.user_id).offset(offset).limit(limit))
        return list(objs.scalars().all())

    async def select_wallets(self, offset: int = 0, limit: int = 100) -> list['WalletModel']:
        objs = await self._async_session.execute(select(WalletModel).offset(offset).limit(limit))
        return list(objs.scalars().all())

    async def select_user_by_email(self, email: str) -> 'UserModel':
        obj = await  self._async_session.execute(select(UserModel).where(UserModel.email == email))
        return obj.scalar_one_or_none()
