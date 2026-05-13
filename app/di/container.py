from typing import Any, AsyncGenerator

from dishka import AsyncContainer, make_async_container, Provider, provide, Scope
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from app.core.settings.jwt import JWTSettings
from app.modules.auth.service.use_cases import ManageTokenService, AuthService, ShowCurrentUserService
from app.unit_of_work.uow import UnitOfWork
from app.database.config import Settings
from app.modules.balances.repository.commands import BalanceCommandsRepository
from app.modules.balances.repository.queries import BalanceQueriesRepository
from app.modules.operations.service.use_cases import DepositBalanceService, TransferBalanceService, \
    WithdrawBalanceService, ExchangeBalanceService
from app.modules.balances.service.use_cases import CreateBalanceService, ManageBalanceService, DeleteBalanceService, \
    ShowBalanceService
from app.modules.transactions.repository.commands import TrnCommandsRepository
from app.modules.transactions.repository.queries import TrnQueriesRepository
from app.modules.transactions.service.use_cases import CreateTrnService, ShowTrnService, UpdateTrnService
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.use_cases import CreateUserService, UpdateUserService, \
    DeleteUserService, ShowUserService, ManageUserService
from app.modules.wallets.repository.commands import WalletCommandsRepository
from app.modules.wallets.repository.queries import WalletQueriesRepository
from app.modules.wallets.service.use_cases import CreateWalletService, UpdateWalletService, DeleteWalletService, \
    ManageWalletService, ShowWalletService


class DBSettingsProvider(Provider):
    """Провайдер по созданию настроек бд"""

    scope = Scope.APP

    @provide
    def db_settings(self) -> Settings:
        return Settings()


class AsyncEngineProvider(Provider):
    """Провайдер по созданию асинхронного движка бд"""

    scope = Scope.APP

    @provide
    def async_engine(self, settings: Settings) -> AsyncEngine:
        return create_async_engine(
            settings.async_database_url,
            echo=False,
        )


class AsyncSessionMakerProvider(Provider):
    """Провайдер по созданию фабрики асинхронных сессий бд"""

    scope = Scope.APP

    @provide
    def async_session_maker(self, async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            async_engine,
            expire_on_commit=False,
        )


class AsyncSessionProvider(Provider):
    """Провайдер для создания асинхронной сессии бд"""

    scope = Scope.REQUEST

    @provide
    async def async_session(self, async_session_maker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, Any]:
        async with async_session_maker() as async_session:
            yield async_session


class UnitOfWorkProvider(Provider):
    """Провайдер для создания надстройки над сессиями бд"""

    scope = Scope.REQUEST

    @provide
    async def uow(self, async_session: AsyncSession) -> AsyncGenerator[UnitOfWork, None]:
        async with UnitOfWork(async_session) as uow:
            yield uow


class CommandsRepositoryProvider(Provider):
    """Провайдер для создания репозиториев команд"""

    scope = Scope.REQUEST

    @provide
    def user_commands(self, async_session: AsyncSession) -> UserCommandsRepository:
        return UserCommandsRepository(async_session)

    @provide
    def wallet_commands(self, async_session: AsyncSession) -> WalletCommandsRepository:
        return WalletCommandsRepository(async_session)

    @provide
    def balance_commands(self, async_session: AsyncSession) -> BalanceCommandsRepository:
        return BalanceCommandsRepository(async_session)

    @provide
    def trn_commands(self, async_session: AsyncSession) -> TrnCommandsRepository:
        return TrnCommandsRepository(async_session)


class QueriesRepositoryProvider(Provider):
    """Провайдер для создания репозиториев запросов"""

    scope = Scope.REQUEST

    @provide
    def user_queries(self, async_session: AsyncSession) -> UserQueriesRepository:
        return UserQueriesRepository(async_session)

    @provide
    def wallet_queries(self, async_session: AsyncSession) -> WalletQueriesRepository:
        return WalletQueriesRepository(async_session)

    @provide
    def balance_queries(self, async_session: AsyncSession) -> BalanceQueriesRepository:
        return BalanceQueriesRepository(async_session)

    @provide
    def trn_queries(self, async_session: AsyncSession) -> TrnQueriesRepository:
        return TrnQueriesRepository(async_session)


class JWTSettingsProvider(Provider):
    """Провайдер по созданию настроек jwt токена"""

    scope = Scope.APP

    @provide
    def jwt_settings(self) -> JWTSettings:
        return JWTSettings()


class ManageTokenServiceProvider(Provider):
    """Провайдер для создания сервисов по работе с токеном"""

    scope = Scope.APP

    @provide
    def manage_service(self, jwt_settings: JWTSettings) -> ManageTokenService:
        return ManageTokenService(jwt_settings)


class AuthServiceProvider(Provider):
    """Провайдер для создания сервиса по аутентификации"""

    scope = Scope.REQUEST

    @provide
    def auth_user(self, user_queries: UserQueriesRepository, manage_service: ManageTokenService) -> AuthService:
        return AuthService(manage_service, user_queries)


class CurrentUserServiceProvider(Provider):
    """Провайдер по созданию сервиса по получению текущего пользователя"""

    scope = Scope.REQUEST

    @provide
    def current_user_service(self, manage_service: ManageTokenService, user_queries: UserQueriesRepository) -> ShowCurrentUserService:
        return ShowCurrentUserService(manage_service, user_queries)


class UserServiceProvider(Provider):
    """Провайдер для создания сервисов пользователя"""

    scope = Scope.REQUEST

    @provide
    def create_service(self, user_commands: UserCommandsRepository) -> CreateUserService:
        return CreateUserService(user_commands)

    @provide
    def update_service(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository) -> UpdateUserService:
        return UpdateUserService(user_commands, user_queries)

    @provide
    def delete_service(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository) -> DeleteUserService:
        return DeleteUserService(user_commands, user_queries)

    @provide
    def show_service(self, user_queries: UserQueriesRepository) -> ShowUserService:
        return ShowUserService(user_queries)

    @provide
    def manage_service(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository) -> ManageUserService:
        return ManageUserService(user_commands, user_queries)


class WalletServiceProvider(Provider):
    """Провайдер для создания сервисов кошельков"""

    scope = Scope.REQUEST

    @provide
    def create_service(self, wallet_commands: WalletCommandsRepository, wallet_queries: WalletQueriesRepository) -> CreateWalletService:
        return CreateWalletService(wallet_commands, wallet_queries)

    @provide
    def update_service(self, wallet_commands: WalletCommandsRepository, wallet_queries: WalletQueriesRepository) -> UpdateWalletService:
        return UpdateWalletService(wallet_commands, wallet_queries)

    @provide
    def delete_service(self, wallet_commands: WalletCommandsRepository, wallet_queries: WalletQueriesRepository) -> DeleteWalletService:
        return DeleteWalletService(wallet_commands, wallet_queries)

    @provide
    def manage_service(self, wallet_commands: WalletCommandsRepository, wallet_queries: WalletQueriesRepository) -> ManageWalletService:
        return ManageWalletService(wallet_commands, wallet_queries)

    @provide
    def show_service(self, wallet_queries: WalletQueriesRepository) -> ShowWalletService:
        return ShowWalletService(wallet_queries)


class TrnServiceProvider(Provider):
    """Провайдер для создания сервисов транзакций"""

    scope = Scope.REQUEST

    @provide
    def create_service(self, trn_commands: TrnCommandsRepository) -> CreateTrnService:
        return CreateTrnService(trn_commands)

    @provide
    def update_service(self, trn_commands: TrnCommandsRepository, trn_queries: TrnQueriesRepository) -> UpdateTrnService:
        return UpdateTrnService(trn_commands, trn_queries)

    @provide
    def show_service(self, trn_queries: TrnQueriesRepository) -> ShowTrnService:
        return ShowTrnService(trn_queries)


class BalanceServiceProvider(Provider):
    """Провайдер для создания сервисов балансов"""

    scope = Scope.REQUEST

    @provide
    def create_service(self, wallet_queries: WalletQueriesRepository, balance_commands: BalanceCommandsRepository, balance_queries: BalanceQueriesRepository) -> CreateBalanceService:
        return CreateBalanceService(wallet_queries, balance_commands, balance_queries)

    @provide
    def manage_service(self, balance_commands: BalanceCommandsRepository, balance_queries: BalanceQueriesRepository) -> ManageBalanceService:
        return ManageBalanceService(balance_commands, balance_queries)

    @provide
    def delete_service(self, balance_commands: BalanceCommandsRepository, balance_queries: BalanceQueriesRepository, wallet_queries: WalletQueriesRepository) -> DeleteBalanceService:
        return DeleteBalanceService(balance_commands, balance_queries, wallet_queries)

    @provide
    def show_service(self, wallet_queries: WalletQueriesRepository, balance_queries: BalanceQueriesRepository) -> ShowBalanceService:
        return ShowBalanceService(wallet_queries, balance_queries)


class OperationServiceProvider(Provider):
    """Провайдер для создания сервисов операций"""

    scope = Scope.REQUEST

    @provide
    def deposit_service(self, wallet_queries: WalletQueriesRepository, balance_commands: BalanceCommandsRepository, balance_queries: BalanceQueriesRepository, create_service: CreateTrnService, update_service: UpdateTrnService) -> DepositBalanceService:
        return DepositBalanceService(wallet_queries, balance_commands, balance_queries, create_service, update_service)

    @provide
    def transfer_service(self, wallet_queries: WalletQueriesRepository, balance_commands: BalanceCommandsRepository, balance_queries: BalanceQueriesRepository, create_service: CreateTrnService, update_service: UpdateTrnService) -> TransferBalanceService:
        return TransferBalanceService(wallet_queries, balance_commands, balance_queries, create_service, update_service)

    @provide
    def withdraw_service(self, wallet_queries: WalletQueriesRepository, balance_commands: BalanceCommandsRepository, balance_queries: BalanceQueriesRepository, create_service: CreateTrnService, update_service: UpdateTrnService) -> WithdrawBalanceService:
        return WithdrawBalanceService(wallet_queries, balance_commands, balance_queries, create_service, update_service)

    @provide
    def exchange_service(self, wallet_queries: WalletQueriesRepository, balance_commands: BalanceCommandsRepository, balance_queries: BalanceQueriesRepository, create_service: CreateTrnService, update_service: UpdateTrnService) -> ExchangeBalanceService:
        return ExchangeBalanceService(wallet_queries, balance_commands, balance_queries, create_service, update_service)


def build_async_container() -> AsyncContainer:
    return make_async_container(
        DBSettingsProvider(),
        AsyncEngineProvider(),
        AsyncSessionMakerProvider(),
        AsyncSessionProvider(),
        UnitOfWorkProvider(),
        CommandsRepositoryProvider(),
        QueriesRepositoryProvider(),
        JWTSettingsProvider(),
        ManageTokenServiceProvider(),
        AuthServiceProvider(),
        UserServiceProvider(),
        WalletServiceProvider(),
        TrnServiceProvider(),
        BalanceServiceProvider(),
        OperationServiceProvider(),
        CurrentUserServiceProvider(),
    )


async_container = build_async_container()
