from pydantic import BaseModel
from decimal import Decimal


class CreateRegularBalanceSchema(BaseModel):
    """Схема по созданию обычного баланса"""

    currency: str
    amount: Decimal
    address: str
    pin: str


class CreateForeignBalanceSchema(BaseModel):
    """Схема по созданию обычного баланса"""

    currency: str
    amount: Decimal
    address: str
    pin: str


class ShowBalancesByWalletSchema(BaseModel):
    """Схема по созданию обычного баланса"""

    address: str
    pin: str
