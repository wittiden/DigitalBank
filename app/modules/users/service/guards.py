from typing import TYPE_CHECKING

from app.common.enums.user_enums import UserStatusesEnum
from app.modules.auth.exceptions import ForbiddenError
from app.modules.users.exceptions import UserIsAlreadyBlockedError, UserIsAlreadyUnBlockedError, UserNotFoundError

if TYPE_CHECKING:
    from app.database.models import UserModel


class UserGuards:
    """Класс для хранения бизнес правил пользователя"""

    @staticmethod
    def require_user_exists(obj: UserModel | None) -> UserModel:
        if not obj:
            raise UserNotFoundError('User not found error')

        return obj

    @staticmethod
    def require_admin(obj: UserModel) -> None:
        if obj.user_status != UserStatusesEnum.ADMIN:
            raise ForbiddenError('Admin privileges required')

    @staticmethod
    def require_user_not_already_blocked(obj: UserModel) -> None:
        if obj.is_blocked:
            raise UserIsAlreadyBlockedError('User is already blocked error')

    @staticmethod
    def require_user_not_already_unblocked(obj: UserModel) -> None:
        if not obj.is_blocked:
            raise UserIsAlreadyUnBlockedError('User is already unblocked error')
