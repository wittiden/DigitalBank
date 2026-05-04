from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository


class UserUnitOfWork:
    """Надстройка над сессиями для сервисов пользователя"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

        self.user_commands = UserCommandsRepository(async_session)
        self.user_queries = UserQueriesRepository(async_session)

    async def __aenter__(self) -> UserUnitOfWork:
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None):
        try:
            if exc_type:
                await self._async_session.rollback()

            else:
                await self._async_session.commit()

        finally:
            await self._async_session.close()

    async def commit(self) -> None:
        await self._async_session.commit()

    async def rollback(self) -> None:
        await self._async_session.rollback()
