from types import TracebackType
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.wallets.repository.commands import WalletCommandsRepository
from app.modules.wallets.repository.queries import WalletQueriesRepository


class WalletUnitOfWork:
    """Надстройка над сессиями для сервисов кошельков"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

        self.wallet_commands = WalletCommandsRepository(async_session)
        self.wallet_queries = WalletQueriesRepository(async_session)

    async def __aenter__(self) -> 'WalletUnitOfWork':
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None):
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

        return False

    async def commit(self) -> None:
        await self._async_session.commit()

    async def rollback(self) -> None:
        await self._async_session.rollback()


class AccountUnitOfWork:
    """Объединенная надстройка пользователей и кошельков над сессиями для сервисов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

        self.wallet_commands = WalletCommandsRepository(async_session)
        self.wallet_queries = WalletQueriesRepository(async_session)
        self.user_commands = UserCommandsRepository(async_session)
        self.user_queries = UserQueriesRepository(async_session)

    async def __aenter__(self) -> 'AccountUnitOfWork':
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool:
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

        return False

    async def commit(self) -> None:
        await self._async_session.commit()

    async def rollback(self) -> None:
        await self._async_session.rollback()


