from enum import Enum


class UserStatusesEnum(str, Enum):
    """Енум для хранения статусов пользователя"""

    UNKNOWN = 'unknown'
    USER = 'user'
    ADMIN = 'admin'
