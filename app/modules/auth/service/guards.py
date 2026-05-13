from typing import TYPE_CHECKING

from app.modules.auth.exceptions import UserIsBlockedError, UserPassNotVerifiedError
from app.modules.auth.service.utils import verify_pass

if TYPE_CHECKING:
    from app.database.models import UserModel


class AuthGuards:
    """Класс для хранения бизнес правил аутентификации пользователя"""

    @staticmethod
    def require_user_not_blocked(obj: 'UserModel') -> None:
        if obj.is_blocked:
            raise UserIsBlockedError('User is blocked error')

    @staticmethod
    def require_verify_pass(password: str, password_hash: str) -> None:
        if not verify_pass(password, password_hash):
            raise UserPassNotVerifiedError('User password != password_hash error')
