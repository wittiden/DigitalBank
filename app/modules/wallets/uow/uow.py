from types import TracebackType
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.wallets.repository.commands import WalletCommandsRepository
from app.modules.wallets.repository.queries import WalletQueriesRepository


class WalletUnitOfWork:
    """Надстройка над сессиями для сервисов кошельков"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

        self.wallet_commands = WalletCommandsRepository(async_session)
        self.wallet_queries = WalletQueriesRepository(async_session)

    def __aenter__(self) -> 'WalletUnitOfWork':
        return self

    def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                  exc_tb: TracebackType | None):
        try:
            if exc_type:
                self._async_session.rollback()

            else:
                self._async_session.commit()

        except Exception:
            self._async_session.rollback()
            raise

        finally:
            self._async_session.close()

        return False

    def commit(self) -> None:
        self._async_session.commit()

    def rollback(self) -> None:
        self._async_session.rollback()
