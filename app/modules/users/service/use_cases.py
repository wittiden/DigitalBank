from typing import Any, TYPE_CHECKING
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.common.decorators import debug_log
from app.common.enums.user_enums import UserStatusesEnum
from app.modules.users.contracts.dtos import FullUserInfoDTO
from app.modules.users.contracts.dtos import SecurityUserInfoDTO
from app.modules.users.exceptions import UserEmailIsExistError, UserPassNotVerifiedError, UserNotFoundError, \
    InvalidFieldError, UserIsBlockedError, UserIsNotBlockedError
from app.modules.users.service.utils import hash_pass, verify_pass

if TYPE_CHECKING:
    from app.database.models.user import UserModel
    from app.modules.users.uow.uow import UserUnitOfWork


class CreateUserService:
    """Сервис по созданию пользователей"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow

    async def _create_entity(self, name: str, email: str, password: str, user_status: UserStatusesEnum) -> 'FullUserInfoDTO':
        password_hash = hash_pass(password)

        try:
            entity: 'UserModel' = await self._user_uow.user_commands.insert_user_info(name=name, email=email,
                                                                                password_hash=password_hash,
                                                                                user_status=user_status)
        except IntegrityError:
            raise UserEmailIsExistError(f'User email ({email}) must be unique')

        await self._user_uow.commit()

        return FullUserInfoDTO.model_validate(entity)

    @debug_log
    async def create_user(self, name: str, email: str, password: str) -> 'FullUserInfoDTO':
        return await self._create_entity(name, email, password, UserStatusesEnum.USER)

    @debug_log
    async def create_admin(self, name: str, email: str, password: str) -> 'FullUserInfoDTO':
        return await self._create_entity(name, email, password, UserStatusesEnum.ADMIN)


class LoginUserService:
    """Сервис по входу в аккаунт для пользователей"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow

    @debug_log
    async def login_user(self, email: str, password: str) -> 'FullUserInfoDTO':
        obj: 'UserModel' = await self._user_uow.user_queries.select_user_by_email(email)

        if not obj:
            raise UserNotFoundError('User not found')

        if not verify_pass(password, obj.password_hash):
            raise UserPassNotVerifiedError('Password != password_hash')

        return FullUserInfoDTO.model_validate(obj)


class DeleteUserService:
    """Сервис по удалению аккаунта пользователя"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow

    @debug_log
    async def delete_user(self, user_id: UUID) -> None:
        obj = await self._user_uow.user_queries.select_user_by_id(user_id)

        if not obj:
            raise UserNotFoundError('User not found')

        await self._user_uow.user_commands.delete_user(obj)

        await self._user_uow.commit()


class UpdateUserService:
    """Сервис по обновлению данных аккаунта пользователя"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow

    @debug_log
    async def portion_update_user(self, email: str, password: str, data: dict[str, Any]) -> 'FullUserInfoDTO':
        obj = await self._user_uow.user_queries.select_user_by_email(email)

        if not obj:
            raise UserNotFoundError('User not found')

        if not verify_pass(password, obj.password_hash):
            raise UserPassNotVerifiedError('Password != password_hash')

        whitelist = ['name', 'email']

        for key, value in data.items():
            if not hasattr(obj, key):
                raise InvalidFieldError('Field not found in user struct')

            if key not in whitelist:
                raise InvalidFieldError('Private field cant change')

        user = await self._user_uow.user_commands.partial_update_user(obj, data)

        await self._user_uow.commit()

        return FullUserInfoDTO.model_validate(user)


class ShowUserService:
    """Сервис по показу информации об аккаунте пользователя"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow

    @debug_log
    async def show_users(self, offset: int = 0, limit: int = 100) -> list['FullUserInfoDTO']:
        objs = await self._user_uow.user_queries.select_users(offset, limit)

        return [FullUserInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_user_by_id(self, user_id: UUID) -> 'FullUserInfoDTO':
        obj = await self._user_uow.user_queries.select_user_by_id(user_id)

        if not obj:
            raise UserNotFoundError('User not found')

        return FullUserInfoDTO.model_validate(obj)

    @debug_log
    async def show_user_by_email(self, email: str) -> 'SecurityUserInfoDTO':
        obj = await self._user_uow.user_queries.select_user_by_email(email)

        if not obj:
            raise UserNotFoundError('User not found')

        return SecurityUserInfoDTO.model_validate(obj)


class ManageUserService:
    """Сервис по менедженгу аккаунта пользователя"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow

    @debug_log
    async def block_user(self, user_id: UUID) -> None:
        obj: 'UserModel' = await self._user_uow.user_queries.select_user_by_id(user_id)

        if not obj:
            raise UserNotFoundError('User not found')

        if obj.is_blocked:
            raise UserIsBlockedError('User was already blocked')

        await self._user_uow.user_commands.partial_update_user(obj, {'is_blocked': True})
        await self._user_uow.commit()

    @debug_log
    async def unblock_user(self, user_id: UUID) -> None:
        obj: 'UserModel' = await self._user_uow.user_queries.select_user_by_id(user_id)

        if not obj:
            raise UserNotFoundError('User not found')

        if not obj.is_blocked:
            raise UserIsNotBlockedError('User was already unblocked')

        await self._user_uow.user_commands.partial_update_user(obj, {'is_blocked': False})
        await self._user_uow.commit()
