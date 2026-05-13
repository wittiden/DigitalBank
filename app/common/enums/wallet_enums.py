from enum import StrEnum


class WalletTypesEnum(StrEnum):
    """Енум для хранения типов кошелька"""

    UNKNOWN = 'unknown'
    DEBIT = 'debit'
    CREDIT = 'credit'
