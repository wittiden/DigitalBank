from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums.user_enums import UserStatusesEnum
from app.database.models.user import UserModel
from app.modules.users.exceptions import InvalidFieldError


class UserCommandsRepository:
    """Репозиторий для управления create, update, delete запросами для пользователя в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_user_info(self, name: str, email: str, password_hash: str, user_status: UserStatusesEnum) -> 'UserModel':
        obj = UserModel(name=name, email=email, password_hash=password_hash, user_status=user_status)
        self._async_session.add(obj)

        try:
            await self._async_session.flush()
            return obj

        except IntegrityError:
            await self._async_session.rollback()
            raise

    async def partial_update_user(self, user: 'UserModel', data: dict[str, Any]) -> 'UserModel':
        for key, value in data.items():
            if not hasattr(user, key):
                raise InvalidFieldError(f'Invalid field {key} error')

            setattr(user, key, value)

        try:
            await self._async_session.flush()
            return user

        except IntegrityError:
            await self._async_session.rollback()
            raise

    async def delete_user(self, user: 'UserModel') -> None:
        await self._async_session.delete(user)

        await self._async_session.flush()
