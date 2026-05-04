from app.common.enums.user_enums import UserStatusesEnum
from app.database.models.user import UserModel
from app.modules.users.contracts.dtos import FullUserInfoDTO
from app.modules.users.service.utils import hash_pass
from app.modules.users.uow.uow import UserUnitOfWork


class CreateUserService:
    """"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow

    async def create_user(self, name: str, email: str, password: str) -> 'FullUserInfoDTO':
        password_hash = hash_pass(password)
        user: 'UserModel' = await self._user_uow.user_commands.insert_user_info(name=name, email=email, password_hash=password_hash, user_status=UserStatusesEnum.USER)

        await self._user_uow.commit()

        return FullUserInfoDTO.model_validate(user)






class LoginUserService:
    """"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow


class DeleteUserService:
    """"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow


class UpdateUserService:
    """"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow


class ShowUserService:
    """"""

    def __init__(self, user_uow: 'UserUnitOfWork') -> None:
        self._user_uow = user_uow