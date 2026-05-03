from enum import Enum


class TransactionTypesEnum(str, Enum):
    """Енум для хранения типов транзакций"""

    UNKNOWN = 'Неизвестный тип транзакции'


class TransactionStatusesEnum(str, Enum):
    """Енум для хранения статусов транзакций"""

    UNKNOWN = 'Неизвестный статус транзакции'