from loguru import logger
import jwt
from jwt import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from app.common.enums.user_enums import UserStatusesEnum
from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.auth.exceptions import TokenInvalidError, ForbiddenError
from app.modules.auth.service.guards import AuthGuards
from app.modules.users.service.guards import UserGuards

if TYPE_CHECKING:
    from app.modules.users.repository.queries import UserQueriesRepository
    from app.core.settings.jwt import JWTSettings
    from app.database.models import UserModel


class ManageTokenService:
    """Сервис по код кодированию и декодированию токенов"""

    def __init__(self, jwt_settings: 'JWTSettings') -> None:
        self._jwt_settings = jwt_settings

    def _public_key(self) -> str:
        return self._jwt_settings.PUBLIC_KEY_PATH.read_text()

    def _private_key(self) -> str:
        return self._jwt_settings.PRIVATE_KEY_PATH.read_text()

    def encode_jwt(self, payload: dict) -> str:
        now = datetime.now(timezone.utc)

        payload.update({
            **payload,
            'iat': now,
            'exp': now + timedelta(minutes=self._jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        })

        return jwt.encode(
            payload=payload,
            key=self._private_key(),
            algorithm=self._jwt_settings.ALGORITHM
        )

    def decode_jwt(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                key=self._public_key(),
                algorithms=[self._jwt_settings.ALGORITHM]
            )
        except InvalidTokenError:
            raise TokenInvalidError('Token invalid error')


class AuthService:
    """Сервис по аутентификации пользователя"""

    def __init__(self, manage_service: 'ManageTokenService', user_queries: 'UserQueriesRepository') -> None:
        self._manage_service = manage_service
        self._user_queries = user_queries

    async def login_user(self, email: str, password: str) -> 'TokenInfoDTO':
        obj: 'UserModel' = await self._user_queries.select_user_by_email(email)

        UserGuards.require_user_exists(obj)
        AuthGuards.require_verify_pass(password, obj.password_hash)
        AuthGuards.require_user_not_blocked(obj)

        token = self._manage_service.encode_jwt({
            'sub': str(obj.user_id),
            'role': obj.user_status.value
        })

        logger.info(f'Вы вошли в аккаунт #{obj.user_id}')
        return TokenInfoDTO(
            token=token
        )


class ShowCurrentUserService:
    """Сервис по показу текущего пользователя"""

    def __init__(self, manage_service: 'ManageTokenService', user_queries: 'UserQueriesRepository') -> None:
        self._manage_service = manage_service
        self._user_queries = user_queries

    async def show_current_user(self, token: str) -> 'UserModel':
        payload = self._manage_service.decode_jwt(token)

        user_id = payload['sub']

        user = await self._user_queries.select_user_by_id(user_id)

        UserGuards.require_user_exists(user)

        return user

    async def show_current_admin(self, token: str) -> 'UserModel':
        payload = self._manage_service.decode_jwt(token)

        user_id = payload['sub']

        user = await self._user_queries.select_user_by_id(user_id)

        if not user.user_status == UserStatusesEnum.ADMIN:
            raise ForbiddenError('Forbidden error')

        UserGuards.require_user_exists(user)

        return user
