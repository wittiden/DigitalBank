from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import UserModel


class UserQueriesRepository:
    """Репозиторий для управления select запросами для пользователя в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_user_by_id(self, user_id: UUID) -> 'UserModel | None':
        return await self._async_session.get(UserModel, user_id)

    async def select_user_by_email(self, email: str) -> 'UserModel | None':
        obj = await self._async_session.execute(select(UserModel).where(UserModel.email == email))
        return obj.scalar_one_or_none()

    async def select_users(self, offset: int = 0, limit: int = 100) -> list['UserModel']:
        objs = await self._async_session.execute(select(UserModel).offset(offset).limit(limit))
        return list(objs.scalars().all())
