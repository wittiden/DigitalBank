from enum import StrEnum


class UserStatusesEnum(StrEnum):
    """Енум для хранения статусов пользователя"""

    UNKNOWN = 'unknown'
    USER = 'user'
    ADMIN = 'admin'
