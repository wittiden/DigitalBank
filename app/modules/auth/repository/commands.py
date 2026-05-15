from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.refresh import RefreshTokenModel
from app.modules.auth.exceptions import InvalidFieldError


class AuthCommandsRepository:
    """Репозиторий для управления create, update, delete запросами для долгосрочных токенов в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_refresh_token_info(self, refresh_token_id: str, user_id: str, expires_at: datetime, created_at: datetime, version: int) -> RefreshTokenModel:
        obj = RefreshTokenModel(refresh_token_id=refresh_token_id, user_id=user_id, expires_at=expires_at, created_at=created_at, version=version)

        self._async_session.add(obj)

        try:
            await self._async_session.flush()
            return obj

        except IntegrityError:
            await self._async_session.rollback()
            raise

    async def partial_update_refresh_token_info(self, refresh_token: RefreshTokenModel, data: dict) -> RefreshTokenModel:
        for key, value in data.items():
            if not hasattr(refresh_token, key):
                raise InvalidFieldError('Invalid field error')

            setattr(refresh_token, key, value)

        try:
            await self._async_session.flush()
            return refresh_token

        except IntegrityError:
            await self._async_session.rollback()
            raise

    async def delete_refresh_token(self, refresh_token: RefreshTokenModel) -> None:
        await self._async_session.delete(refresh_token)

        await self._async_session.flush()
