from typing import Any, TYPE_CHECKING
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from loguru import logger

from app.common.decorators import debug_log
from app.common.enums.user_enums import UserStatusesEnum
from app.modules.auth.service.utils import verify_pass
from app.modules.users.contracts.dtos import FullUserInfoDTO
from app.modules.users.contracts.dtos import SecurityUserInfoDTO
from app.modules.users.exceptions import UserEmailIsExistError, \
    InvalidFieldError, UserPassesIsTheSame
from app.modules.users.service.guards import UserGuards
from app.modules.users.service.utils import hash_pass

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


class DeleteUserService:
    """Сервис по удалению аккаунта пользователя"""

    def __init__(self, user_commands: 'UserCommandsRepository', user_queries: 'UserQueriesRepository') -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries

    @debug_log
    async def delete_user_by_id(self, current_user: 'UserModel', user_id: UUID) -> None:
        UserGuards.require_admin(current_user)

        obj = await self._user_queries.select_user_by_id(user_id)

        UserGuards.require_user_exists(obj)

        await self._user_commands.delete_user(obj)

        logger.info(f'Пользователь #{user_id} удален')

    @debug_log
    async def close_my_user(self, current_user: 'UserModel') -> None:
        UserGuards.require_user_exists(current_user)

        await self._user_commands.delete_user(current_user)

        logger.info(f'Пользователь {current_user.user_id} удален')


class UpdateUserService:
    """Сервис по обновлению данных аккаунта пользователя"""

    def __init__(self, user_commands: 'UserCommandsRepository', user_queries: 'UserQueriesRepository') -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries

    @debug_log
    async def partial_update_my_user(self, current_user: 'UserModel', data: dict[str, Any]) -> 'SecurityUserInfoDTO':
        UserGuards.require_user_exists(current_user)

        if 'password' in data.keys():
            if verify_pass(data['password'], current_user.password_hash):
                raise UserPassesIsTheSame('User old_pass == new_pass')

            password_hash = hash_pass(data['password'])

            data.pop('password')
            data['password_hash'] = password_hash

        try:
            current_user = await self._user_commands.partial_update_user(current_user, data)
        except IntegrityError:
            raise UserEmailIsExistError(f'User email ({current_user.email}) must be unique')

        logger.info(f'Данные пользователя #{current_user.user_id} обновлены')
        return SecurityUserInfoDTO.model_validate(current_user)


class ShowUserService:
    """Сервис по показу информации об аккаунте пользователя"""

    def __init__(self, user_queries: 'UserQueriesRepository') -> None:
        self._user_queries = user_queries

    @debug_log
    async def show_users(self, current_user: 'UserModel', offset: int = 0, limit: int = 100) -> list['FullUserInfoDTO']:
        UserGuards.require_admin(current_user)

        objs = await self._user_queries.select_users(offset, limit)

        return [FullUserInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_user_by_id(self, current_user: 'UserModel', user_id: UUID) -> 'FullUserInfoDTO':
        UserGuards.require_admin(current_user)

        obj = await self._user_queries.select_user_by_id(user_id)

        UserGuards.require_user_exists(obj)

        return FullUserInfoDTO.model_validate(obj)

    @debug_log
    async def show_my_user(self, current_user: 'UserModel') -> 'SecurityUserInfoDTO':
        UserGuards.require_user_exists(current_user)

        return SecurityUserInfoDTO.model_validate(current_user)


class ManageUserService:
    """Сервис по менедженгу аккаунта пользователя"""

    def __init__(self, user_commands: 'UserCommandsRepository', user_queries: 'UserQueriesRepository') -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries

    @debug_log
    async def block_user(self, current_user: 'UserModel', user_id: UUID) -> None:
        UserGuards.require_admin(current_user)

        obj: 'UserModel' = await self._user_queries.select_user_by_id(user_id)

        UserGuards.require_user_exists(obj)
        UserGuards.require_user_not_already_blocked(obj)

        await self._user_commands.partial_update_user(obj, {'is_blocked': True})

        logger.info(f'Пользователь #{obj.user_id} заблокирован')


    @debug_log
    async def unblock_user(self, current_user: 'UserModel', user_id: UUID) -> None:
        UserGuards.require_admin(current_user)

        obj: 'UserModel' = await self._user_queries.select_user_by_id(user_id)

        UserGuards.require_user_exists(obj)
        UserGuards.require_user_not_already_unblocked(obj)

        await self._user_commands.partial_update_user(obj, {'is_blocked': False})

        logger.info(f'Пользователь #{obj.user_id} разблокирован')
