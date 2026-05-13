from enum import StrEnum


class BalanceTypesEnum(StrEnum):
    """Енум для хранения типов балансов"""

    UNKNOWN = 'unknown'
    REGULAR = 'regular'
    FOREIGN = 'foreign'
