from enum import Enum


class BalanceTypesEnum(str, Enum):
    """Енум для хранения типов балансов"""

    UNKNOWN = 'unknown'
    REGULAR = 'regular'
    FOREIGN = 'foreign'

