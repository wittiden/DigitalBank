from typing import TYPE_CHECKING

from app.modules.users.exceptions import UserNotFoundError, UserIsBlockedError, UserIsNotBlockedError, \
    UserPassNotVerifiedError
from app.modules.users.service.utils import verify_pass

if TYPE_CHECKING:
    from app.database.models import UserModel


class UserGuards:
    """Класс для хранения бизнес правил пользователя"""

    @staticmethod
    def require_user_exists(obj: 'UserModel') -> None:
        if not obj:
            raise UserNotFoundError('User not found')

    @staticmethod
    def require_user_not_blocked(obj: 'UserModel') -> None:
        if obj.is_blocked:
            raise UserIsBlockedError('User is blocked')

    @staticmethod
    def require_user_not_unblocked(obj: 'UserModel') -> None:
        if not obj.is_blocked:
            raise UserIsNotBlockedError('User is unblocked')

    @staticmethod
    def require_verify_pass(password: str, password_hash: str) -> None:
        if not verify_pass(password, password_hash):
            raise UserPassNotVerifiedError('User password != password_hash')