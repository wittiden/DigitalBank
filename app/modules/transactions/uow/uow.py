from types import TracebackType
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transactions.repository.commands import TrnCommandsRepository
from app.modules.transactions.repository.queries import TrnQueriesRepository


class TrnUnitOfWork:
    """Надстройка над сессиями для сервисов транзакций"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

        self.trn_commands = TrnCommandsRepository(self._async_session)
        self.trn_queries = TrnQueriesRepository(self._async_session)

    async def __aenter__(self) -> 'TrnUnitOfWork':
        return self

    async def __aexit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> None:
        try:
            if exc_type:
                await self._async_session.rollback()

            else:
                await self._async_session.commit()

        except Exception:
            await self._async_session.rollback()
            raise

        finally:
            await self._async_session.close()

    async def commit(self) -> None:
        await self._async_session.commit()

    async def rollback(self) -> None:
        await self._async_session.rollback()
