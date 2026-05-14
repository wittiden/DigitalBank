from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums.balance_enums import BalanceTypesEnum
from app.database.models import BalanceModel
from app.modules.balances.exceptions import InvalidFieldError


class BalanceCommandsRepository:
    """Репозиторий для управления create, update, delete запросами для балансов в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_balance_info(self, currency: str, amount: Decimal, balance_type: BalanceTypesEnum, wallet_id: UUID) -> 'BalanceModel':
        obj = BalanceModel(currency=currency, amount=amount, balance_type=balance_type, wallet_id=wallet_id)

        self._async_session.add(obj)

        try:
            await self._async_session.flush()
            return obj

        except IntegrityError:
            await self._async_session.rollback()
            raise

    async def partial_update_balance(self, balance: 'BalanceModel', data: dict[str, Any]) -> 'BalanceModel':
        for key, value in data.items():
            if not hasattr(balance, key):
                raise InvalidFieldError(f'invalid filed {key} error')

            setattr(balance, key, value)

        try:
            await self._async_session.flush()
            return balance

        except IntegrityError:
            await self._async_session.rollback()
            raise

    async def delete_balance(self, balance: 'BalanceModel') -> None:
        await self._async_session.delete(balance)

        await self._async_session.flush()
