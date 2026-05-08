from typing import Any, TYPE_CHECKING
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from loguru import logger

from app.common.decorators import debug_log
from app.common.enums.user_enums import UserStatusesEnum
from app.modules.users.contracts.dtos import FullUserInfoDTO
from app.modules.users.contracts.dtos import SecurityUserInfoDTO
from app.modules.users.exceptions import UserEmailIsExistError, \
    InvalidFieldError, UserPassesIsTheSame
from app.modules.users.service.guards import UserGuards
from app.modules.users.service.utils import hash_pass, verify_pass

if TYPE_CHECKING:
    from app.database.models.user import UserModel
    from app.modules.users.repository.commands import UserCommandsRepository
    from app.modules.users.repository.queries import UserQueriesRepository


class CreateUserService:
    """Сервис по созданию пользователей"""

    def __init__(self, user_commands: 'UserCommandsRepository') -> None:
        self._user_commands = user_commands

    async def _create_entity(self, name: str, email: str, password: str, user_status: UserStatusesEnum) -> 'SecurityUserInfoDTO':
        password_hash = hash_pass(password)

        try:
            entity: 'UserModel' = await self._user_commands.insert_user_info(name=name, email=email,
                                                                                password_hash=password_hash,
                                                                                user_status=user_status)
        except IntegrityError:
            raise UserEmailIsExistError(f'User email ({email}) must be unique')

        logger.info(f'Пользователь #{entity.user_id} создан')
        return SecurityUserInfoDTO.model_validate(entity)

    @debug_log
    async def create_user(self, name: str, email: str, password: str) -> 'SecurityUserInfoDTO':
        return await self._create_entity(name, email, password, UserStatusesEnum.USER)

    @debug_log
    async def create_admin(self, name: str, email: str, password: str) -> 'SecurityUserInfoDTO':
        return await self._create_entity(name, email, password, UserStatusesEnum.ADMIN)


class LoginUserService:
    """Сервис по входу в аккаунт для пользователей"""

    def __init__(self, user_queries: 'UserQueriesRepository') -> None:
        self._user_queries = user_queries

    @debug_log
    async def login_user(self, email: str, password: str) -> 'SecurityUserInfoDTO':
        obj: 'UserModel' = await self._user_queries.select_user_by_email(email)

        UserGuards.require_user_exists(obj)
        UserGuards.require_verify_pass(password, obj.password_hash)

        logger.info(f'Вы вошли в аккаунт #{obj.user_id}')
        return SecurityUserInfoDTO.model_validate(obj)


class DeleteUserService:
    """Сервис по удалению аккаунта пользователя"""

    def __init__(self, user_commands: 'UserCommandsRepository', user_queries: 'UserQueriesRepository') -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries

    @debug_log
    async def delete_user_by_id(self, user_id: UUID) -> None:
        obj = await self._user_queries.select_user_by_id(user_id)

        UserGuards.require_user_exists(obj)

        await self._user_commands.delete_user(obj)

        logger.info(f'Пользователь #{user_id} удален')

    async def close_user(self, email: str, password: str) -> None:
        obj: 'UserModel' = await self._user_queries.select_user_by_email(email)

        UserGuards.require_user_exists(obj)
        UserGuards.require_verify_pass(password, obj.password_hash)

        await self._user_commands.delete_user(obj)

        logger.info(f'Пользователь {email} удален')


class UpdateUserService:
    """Сервис по обновлению данных аккаунта пользователя"""

    def __init__(self, user_commands: 'UserCommandsRepository', user_queries: 'UserQueriesRepository') -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries

    @debug_log
    async def partial_update_user(self, email: str, password: str, data: dict[str, Any]) -> 'SecurityUserInfoDTO':
        obj: 'UserModel' = await self._user_queries.select_user_by_email(email)

        UserGuards.require_user_exists(obj)
        UserGuards.require_verify_pass(password, obj.password_hash)
        UserGuards.require_user_not_blocked(obj)

        if 'password' in data.keys():
            password_hash = hash_pass(data['password'])

            if verify_pass(password, password_hash):
                raise UserPassesIsTheSame('User old_pass == new_pass')

            data.pop('password')
            data['password_hash'] = password_hash

        whitelist = ['name', 'email', 'password_hash']

        for key, value in data.items():

            if key not in whitelist:
                raise InvalidFieldError('Private field cant change')

        try:
            user = await self._user_commands.partial_update_user(obj, data)
        except IntegrityError:
            raise UserEmailIsExistError(f'User email ({email}) must be unique')

        logger.info(f'Данные пользователя #{user.user_id} обновлены')
        return SecurityUserInfoDTO.model_validate(user)


class ShowUserService:
    """Сервис по показу информации об аккаунте пользователя"""

    def __init__(self, user_queries: 'UserQueriesRepository') -> None:
        self._user_queries = user_queries

    @debug_log
    async def show_users(self, offset: int = 0, limit: int = 100) -> list['FullUserInfoDTO']:
        objs = await self._user_queries.select_users(offset, limit)

        return [FullUserInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_user_by_id(self, user_id: UUID) -> 'FullUserInfoDTO':
        obj = await self._user_queries.select_user_by_id(user_id)

        UserGuards.require_user_exists(obj)

        return FullUserInfoDTO.model_validate(obj)

    @debug_log
    async def show_my_user(self, email: str, password: str) -> 'SecurityUserInfoDTO':
        obj: 'UserModel' = await self._user_queries.select_user_by_email(email)

        UserGuards.require_user_exists(obj)
        UserGuards.require_verify_pass(password, obj.password_hash)

        return SecurityUserInfoDTO.model_validate(obj)


class ManageUserService:
    """Сервис по менедженгу аккаунта пользователя"""

    def __init__(self, user_commands: 'UserCommandsRepository', user_queries: 'UserQueriesRepository') -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries

    @debug_log
    async def block_user(self, user_id: UUID) -> None:
        obj: 'UserModel' = await self._user_queries.select_user_by_id(user_id)

        UserGuards.require_user_exists(obj)
        UserGuards.require_user_not_blocked(obj)

        await self._user_commands.partial_update_user(obj, {'is_blocked': True})

        logger.info(f'Пользователь #{obj.user_id} заблокирован')


    @debug_log
    async def unblock_user(self, user_id: UUID) -> None:
        obj: 'UserModel' = await self._user_queries.select_user_by_id(user_id)

        UserGuards.require_user_exists(obj)
        UserGuards.require_user_not_unblocked(obj)

        await self._user_commands.partial_update_user(obj, {'is_blocked': False})

        logger.info(f'Пользователь #{obj.user_id} разблокирован')
