from decimal import Decimal

from pydantic import BaseModel


class CreateBalanceSchema(BaseModel):
    """Схема по созданию баланса"""

    currency: str
    amount: Decimal
    address: str
    pin: str


class CloseBalanceSchema(BaseModel):
    """Схема по закрытию баланса"""

    address: str
    pin: str
    currency: str


# class ShowBalancesByWalletSchema(BaseModel):
#     """Схема по созданию обычного баланса"""
#
#     address: str
#     pin: str
