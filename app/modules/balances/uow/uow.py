from types import TracebackType
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.balances.repository.commands import BalanceCommandsRepository
from app.modules.balances.repository.queries import BalanceQueriesRepository
from app.modules.wallets.repository.commands import WalletCommandsRepository
from app.modules.wallets.repository.queries import WalletQueriesRepository


class BalanceUnitOfWork:
    """Надстройка над сессиями для сервисов балансов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

        self.balance_commands = BalanceCommandsRepository(self._async_session)
        self.balance_queries = BalanceQueriesRepository(self._async_session)

    async def __aenter__(self) -> 'BalanceUnitOfWork':
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


class OperationUnitOfWork:
    """Объединенная надстройка кошельков и балансов над сессиями для сервисов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

        self.balance_commands = BalanceCommandsRepository(self._async_session)
        self.balance_queries = BalanceQueriesRepository(self._async_session)
        self.wallet_commands = WalletCommandsRepository(self._async_session)
        self.wallet_queries = WalletQueriesRepository(self._async_session)

    async def __aenter__(self) -> 'OperationUnitOfWork':
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
