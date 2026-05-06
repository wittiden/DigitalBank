from decimal import Decimal
from typing import Any, TYPE_CHECKING
from uuid import UUID
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.common.enums.balance_enums import BalanceTypesEnum
from app.modules.balances.contracts.dtos import SecurityBalanceInfoDTO
from app.modules.balances.exceptions import BalanceCurrencyIsExistError
from app.modules.balances.service.guards import BalanceGuards
from app.modules.wallets.service.guards import WalletGuards

if TYPE_CHECKING:
    from app.modules.balances.uow.uow import BalanceUnitOfWork
    from app.modules.balances.uow.uow import OperationUnitOfWork
    from app.database.models import WalletModel


class CreateBalanceService:
    """Сервис по созданию балансов"""

    def __init__(self, operation_uow: 'OperationUnitOfWork') -> None:
        self._operation_uow = operation_uow

    async def _create_balance(self, currency: str, amount: Decimal, balance_type: BalanceTypesEnum, address: str, pin: str) -> 'SecurityBalanceInfoDTO':
        obj: 'WalletModel' = await self._operation_uow.wallet_queries.select_wallet_by_address(address)

        WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_verify_pin(pin, obj.pin_hash)
        WalletGuards.require_wallet_not_blocked(obj)

        try:
            balance = await self._operation_uow.balance_commands.insert_balance_info(currency, amount, balance_type)
        except IntegrityError:
            raise BalanceCurrencyIsExistError(f'Balance currency {currency} is exist error')

        balance_count = self._operation_uow.balance_queries.select_balances_count(balance.wallet_id)
        BalanceGuards.require_balance_limit(balance_count)

        await self._operation_uow.commit()

        logger.info(f'Баланс привязанный к адресу {address} создан')
        return SecurityBalanceInfoDTO.model_validate(balance)

    async def create_regular_balance(self, currency: str, amount: Decimal, address: str, pin: str) -> 'SecurityBalanceInfoDTO':
        return await self._create_balance(currency, amount, BalanceTypesEnum.REGULAR, address, pin)

    async def create_foreign_balance(self, currency: str, amount: Decimal, address: str, pin: str) -> 'SecurityBalanceInfoDTO':
        return await self._create_balance(currency, amount, BalanceTypesEnum.FOREIGN, address, pin)


class ManageBalanceService:
    """Сервис по менедженгу балансов"""

    def __init__(self, balance_uow: 'BalanceUnitOfWork') -> None:
        self._balance_uow = balance_uow

    async def freeze_balance(self, balance_id: UUID) -> None:
        obj = await self._balance_uow.balance_queries.select_balance_by_id(balance_id)

        BalanceGuards.require_balance_exist(obj)
        BalanceGuards.require_balance_not_frozen(obj)

        await self._balance_uow.balance_commands.partial_update_balance(obj, {'is_frozen': True})

        await self._balance_uow.commit()
        logger.info(f'Баланс #{balance_id} заморожен')

    async def unfreeze_balance(self, balance_id: UUID) -> None:
        obj = await self._balance_uow.balance_queries.select_balance_by_id(balance_id)

        BalanceGuards.require_balance_exist(obj)
        BalanceGuards.require_balance_not_unfrozen(obj)

        await self._balance_uow.balance_commands.partial_update_balance(obj, {'is_frozen': False})

        await self._balance_uow.commit()
        logger.info(f'Баланс #{balance_id} разморожен')


class UpdateBalanceService:
    """Сервис по обновлению данных балансов"""

    def __init__(self, operation_uow: 'OperationUnitOfWork') -> None:
        self._operation_uow = operation_uow

    # def update_balance(self, balance_id: UUID, data: dict[str, Any]) -> 'SecurityBalanceInfoDTO':
    #     obj = self._operation_uow.balance_queries(balance_id)
    #
    #     BalanceGuards.require_balance_exist(obj)
    #
    #     whitelist = ['amount']
    #
    #     for key, value in data.items():
    #         if key not in whitelist:
    #             raise
    #
    #         if not hasattr(obj, key):
    #             raise
    #
    #


class DeleteBalanceService:
    """Сервис по удалению балансов"""

    def __init__(self, balance_uow: 'BalanceUnitOfWork') -> None:
        self._balance_uow = balance_uow

    async def delete_balance(self, balance_id: UUID) -> None:
        obj = await self._balance_uow.balance_queries.select_balance_by_id(balance_id)

        BalanceGuards.require_balance_exist(obj)

        await self._balance_uow.balance_commands.delete_balance(obj)

        await self._balance_uow.commit()
        logger.info(f'Баланс {balance_id} удален')


class ShowBalanceService:
    """Сервис по показу данных балансов"""

    def __init__(self, balance_uow: 'BalanceUnitOfWork') -> None:
        self._balance_uow = balance_uow


class DepositBalanceService:
    """Сервис по пополнению баланса"""

    def __init__(self, operation_uow: 'OperationUnitOfWork') -> None:
        self._operation_uow = operation_uow


class WithdrawBalanceService:
    """Сервис по снятию денег с баланса"""

    def __init__(self, operation_uow: 'OperationUnitOfWork') -> None:
        self._operation_uow = operation_uow


class ExchangeBalanceService:
    """Сервис по обмену валют на или между балансами"""

    def __init__(self, operation_uow: 'OperationUnitOfWork') -> None:
        self._operation_uow = operation_uow