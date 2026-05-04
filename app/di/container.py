from typing import Any, AsyncGenerator

from dishka import AsyncContainer, make_async_container, Provider, provide, Scope
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from app.database.config import settings
from app.modules.users.service.use_cases import CreateUserService, LoginUserService, UpdateUserService, \
    DeleteUserService, ShowUserService
from app.modules.users.uow.uow import UserUnitOfWork


class AsyncEngineProvider(Provider):
    """Провайдер по созданию асинхронного движка бд"""

    scope = Scope.APP

    @provide
    def async_engine(self) -> AsyncEngine:
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
    async def user_uow(self, async_session: AsyncSession) -> AsyncGenerator[UserUnitOfWork, None]:
        async with UserUnitOfWork(async_session) as user_uow:
            yield user_uow


class UserServiceProvider(Provider):
    """Провайдер для создания сервисов пользователя"""

    scope = Scope.REQUEST

    @provide
    def create_service(self, user_uow: UserUnitOfWork) -> CreateUserService:
        return CreateUserService(user_uow)

    @provide
    def login_service(self, user_uow: UserUnitOfWork) -> LoginUserService:
        return LoginUserService(user_uow)

    @provide
    def update_service(self, user_uow: UserUnitOfWork) -> UpdateUserService:
        return UpdateUserService(user_uow)

    @provide
    def delete_service(self, user_uow: UserUnitOfWork) -> DeleteUserService:
        return DeleteUserService(user_uow)

    @provide
    def show_service(self, user_uow: UserUnitOfWork) -> ShowUserService:
        return ShowUserService(user_uow)


def build_async_container() -> AsyncContainer:
    return make_async_container(
        AsyncEngineProvider(),
        AsyncSessionMakerProvider(),
        AsyncSessionProvider(),
        UnitOfWorkProvider(),
        UserServiceProvider()
    )


async_container = build_async_container()