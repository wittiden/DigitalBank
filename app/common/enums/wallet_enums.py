from enum import Enum


class WalletTypesEnum(str, Enum):
    """Енум для хранения типов кошелька"""

    UNKNOWN = 'unknown'
    DEBIT = 'debit'
    CREDIT = 'credit'

