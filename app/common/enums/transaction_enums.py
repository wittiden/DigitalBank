from enum import StrEnum


class TransactionTypesEnum(StrEnum):
    """Енум для хранения типов транзакций"""

    UNKNOWN = 'unknown'
    DEPOSIT = 'deposit'
    WITHDRAW = 'withdraw'
    EXCHANGE = 'exchange'
    TRANSFER = 'transfer'


class TransactionStatusesEnum(StrEnum):
    """Енум для хранения статусов транзакций"""

    UNKNOWN = 'unknown'
    FAILED = 'failed'
    PENDING = 'pending'
    SUCCESS = 'success'
