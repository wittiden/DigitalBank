from enum import Enum


class TransactionTypesEnum(str, Enum):
    """Енум для хранения типов транзакций"""

    UNKNOWN = 'unknown'
    DEPOSIT = 'deposit'
    WITHDRAW = 'withdraw'
    EXCHANGE = 'exchange'
    TRANSFER = 'transfer'


class TransactionStatusesEnum(str, Enum):
    """Енум для хранения статусов транзакций"""

    UNKNOWN = 'unknown'
    FAILED = 'failed'
    PENDING = 'pending'
    SUCCESS = 'success'
