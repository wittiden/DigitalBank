from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from uuid import uuid4

import jwt
from jwt import InvalidTokenError
from loguru import logger

from app.common.enums.user_enums import UserStatusesEnum
from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.auth.exceptions import ForbiddenError, OldTokenError, RevokedTokenError, TokenInvalidError
from app.modules.auth.repository.commands import AuthCommandsRepository
from app.modules.auth.repository.queries import AuthQueriesRepository
from app.modules.auth.service.guards import AuthGuards
from app.modules.users.service.guards import UserGuards

if TYPE_CHECKING:
    from app.core.settings.jwt import JWTSettings
    from app.database.models import UserModel
    from app.modules.users.repository.queries import UserQueriesRepository


class ManageTokenService:
    """Сервис по код кодированию и декодированию токенов"""

    def __init__(self, jwt_settings: 'JWTSettings', auth_commands: 'AuthCommandsRepository') -> None:
        self._jwt_settings = jwt_settings
        self._auth_commands = auth_commands

    def _access_public_token(self) -> str:
        return self._jwt_settings.ACCESS_PUBLIC_KEY_PATH.read_text()

    def _access_private_token(self) -> str:
        return self._jwt_settings.ACCESS_PRIVATE_KEY_PATH.read_text()

    def _refresh_public_token(self) -> str:
        return self._jwt_settings.REFRESH_PUBLIC_KEY_PATH.read_text()

    def _refresh_private_token(self) -> str:
        return self._jwt_settings.REFRESH_PRIVATE_KEY_PATH.read_text()

    def encode_access_token(self, payload: dict) -> str:
        now = datetime.now(UTC)

        payload.update({**payload, 'iat': now, 'exp': now + timedelta(minutes=self._jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES)})

        return jwt.encode(payload=payload, key=self._access_private_token(), algorithm=self._jwt_settings.ACCESS_ALGORITHM)

    async def encode_refresh_token(self, payload: dict) -> str:
        now = datetime.now(UTC)
        token_id = str(uuid4())

        payload.update({**payload, 'jti': token_id, 'iat': now, 'exp': now + timedelta(days=self._jwt_settings.REFRESH_TOKEN_EXPIRE_DAYS)})

        await self._auth_commands.insert_refresh_token_info(
            refresh_token_id=payload['jti'], user_id=payload['sub'], expires_at=payload['exp'], created_at=payload['iat'], version=self._jwt_settings.REFRESH_TOKEN_VERSION
        )

        return jwt.encode(payload=payload, key=self._refresh_private_token(), algorithm=self._jwt_settings.REFRESH_ALGORITHM)

    def decode_access_token(self, access_token: str) -> dict:
        try:
            return jwt.decode(access_token, key=self._access_public_token(), algorithms=[self._jwt_settings.ACCESS_ALGORITHM])

        except InvalidTokenError as err:
            raise TokenInvalidError('Invalid token error') from err

    def decode_refresh_token(self, refresh_token: str) -> dict:
        try:
            return jwt.decode(refresh_token, key=self._refresh_public_token(), algorithms=[self._jwt_settings.REFRESH_ALGORITHM])

        except InvalidTokenError as err:
            raise TokenInvalidError('Invalid token error') from err


class AuthService:
    """Сервис по аутентификации пользователя"""

    def __init__(
        self,
        manage_service: 'ManageTokenService',
        user_queries: 'UserQueriesRepository',
        auth_commands: 'AuthCommandsRepository',
        auth_queries: 'AuthQueriesRepository',
        jwt_settings: JWTSettings,
    ) -> None:
        self._manage_service = manage_service
        self._user_queries = user_queries
        self._auth_commands = auth_commands
        self._auth_queries = auth_queries
        self._jwt_settings = jwt_settings

    async def login_user(self, email: str, password: str) -> 'TokenInfoDTO':
        obj = await self._user_queries.select_user_by_email(email)

        obj = UserGuards.require_user_exists(obj)
        AuthGuards.require_verify_pass(password, obj.password_hash)
        AuthGuards.require_user_not_blocked(obj)

        access_token = self._manage_service.encode_access_token({'sub': str(obj.user_id), 'role': obj.user_status, 'type': 'access'})
        refresh_token = await self._manage_service.encode_refresh_token({'sub': str(obj.user_id), 'type': 'refresh'})

        logger.info(f'Вы вошли в аккаунт #{obj.user_id}')
        return TokenInfoDTO(access_token=access_token, refresh_token=refresh_token)

    async def logout_user(self, user: 'UserModel') -> None:
        tokens = await self._auth_queries.select_refresh_tokens_by_user_id(user.user_id)

        now = datetime.now(UTC)

        for token in tokens:
            await self._auth_commands.partial_update_refresh_token_info(token, {'revoked_at': now})

        logger.info(f'Все токены пользователя #{user.user_id} были сожжены')

    async def refresh_tokens(self, refresh_token: str) -> TokenInfoDTO:
        payload = self._manage_service.decode_refresh_token(refresh_token)

        jti = payload['jti']

        obj = await self._auth_queries.select_refresh_token_by_id(jti)
        obj = AuthGuards.require_refresh_token_exist(obj)

        if obj.revoked_at is not None:
            raise RevokedTokenError('Revoked token error')

        if obj.version != self._jwt_settings.REFRESH_TOKEN_VERSION:
            raise OldTokenError('Old token error')

        user_id = payload['sub']

        user = await self._user_queries.select_user_by_id(user_id)
        user = UserGuards.require_user_exists(user)
        AuthGuards.require_user_not_blocked(user)

        access_token = self._manage_service.encode_access_token({'sub': payload['sub'], 'role': user.user_status, 'type': 'access'})

        return TokenInfoDTO(access_token=access_token, refresh_token=refresh_token)


class ShowCurrentUserService:
    """Сервис по показу текущего пользователя"""

    def __init__(self, manage_service: 'ManageTokenService', user_queries: 'UserQueriesRepository') -> None:
        self._manage_service = manage_service
        self._user_queries = user_queries

    async def show_current_user(self, token: str) -> 'UserModel':
        payload = self._manage_service.decode_access_token(token)

        user_id = payload['sub']

        user = await self._user_queries.select_user_by_id(user_id)

        user = UserGuards.require_user_exists(user)

        return user

    async def show_current_admin(self, token: str) -> 'UserModel':
        payload = self._manage_service.decode_access_token(token)

        user_id = payload['sub']

        user = await self._user_queries.select_user_by_id(user_id)

        user = UserGuards.require_user_exists(user)

        if not user.user_status == UserStatusesEnum.ADMIN:
            raise ForbiddenError('Forbidden error')

        return user
