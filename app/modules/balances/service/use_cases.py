from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID
from loguru import logger

from app.common.decorators import debug_log
from app.common.enums.balance_enums import BalanceTypesEnum
from app.modules.balances.contracts.dtos import FullBalanceInfoDTO
from app.modules.balances.contracts.dtos import SecurityBalanceInfoDTO
from app.modules.balances.service.guards import BalanceGuards
from app.modules.wallets.service.guards import WalletGuards

if TYPE_CHECKING:
    from app.database.models import WalletModel
    from app.database.models import BalanceModel
    from app.modules.wallets.repository.queries import WalletQueriesRepository
    from app.modules.balances.repository.commands import BalanceCommandsRepository
    from app.modules.balances.repository.queries import BalanceQueriesRepository


class CreateBalanceService:
    """Сервис по созданию балансов"""

    def __init__(self, wallet_queries: 'WalletQueriesRepository', balance_commands: 'BalanceCommandsRepository', balance_queries: 'BalanceQueriesRepository') -> None:
        self._wallet_queries = wallet_queries
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries

    async def _create_balance(self, currency: str, amount: Decimal, balance_type: BalanceTypesEnum, address: str, pin: str) -> 'SecurityBalanceInfoDTO':
        obj: 'WalletModel' = await self._wallet_queries.select_wallet_by_address(address)

        WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_verify_pin(pin, obj.pin_hash)
        WalletGuards.require_wallet_not_blocked(obj)

        balance = await self._balance_commands.insert_balance_info(currency, amount, balance_type, obj.wallet_id)

        balance_count: int = await self._balance_queries.select_balances_count(balance.wallet_id)
        BalanceGuards.require_balance_limit(balance_count)

        logger.info(f'Баланс привязанный к адресу {address} создан')
        return SecurityBalanceInfoDTO.model_validate(balance)

    @debug_log
    async def create_regular_balance(self, currency: str, amount: Decimal, address: str, pin: str) -> 'SecurityBalanceInfoDTO':
        return await self._create_balance(currency, amount, BalanceTypesEnum.REGULAR, address, pin)

    @debug_log
    async def create_foreign_balance(self, currency: str, amount: Decimal, address: str, pin: str) -> 'SecurityBalanceInfoDTO':
        return await self._create_balance(currency, amount, BalanceTypesEnum.FOREIGN, address, pin)


class ManageBalanceService:
    """Сервис по менедженгу балансов"""

    def __init__(self, balance_commands: 'BalanceCommandsRepository', balance_queries: 'BalanceQueriesRepository') -> None:
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries

    @debug_log
    async def freeze_balance(self, balance_id: UUID) -> None:
        obj = await self._balance_queries.select_balance_by_id(balance_id)

        BalanceGuards.require_balance_exist(obj)
        BalanceGuards.require_balance_not_frozen(obj)

        await self._balance_commands.partial_update_balance(obj, {'is_frozen': True})

        logger.info(f'Баланс #{balance_id} заморожен')

    @debug_log
    async def unfreeze_balance(self, balance_id: UUID) -> None:
        obj = await self._balance_queries.select_balance_by_id(balance_id)

        BalanceGuards.require_balance_exist(obj)
        BalanceGuards.require_balance_not_unfrozen(obj)

        await self._balance_commands.partial_update_balance(obj, {'is_frozen': False})

        logger.info(f'Баланс #{balance_id} разморожен')


class UpdateBalanceService:
    """Сервис по обновлению информации баланса"""

    def __init__(self, balance_commands: 'BalanceCommandsRepository', balance_queries: 'BalanceQueriesRepository') -> None:
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries

    async def update_balance_amount(self, balance_id: UUID, new_amount: Decimal) -> 'BalanceModel':
        balance: 'BalanceModel' = await self._balance_queries.select_balance_by_id(balance_id)
        BalanceGuards.require_balance_exist(balance)
        BalanceGuards.require_balance_not_frozen(balance)

        await self._balance_commands.partial_update_balance(balance, {'amount': new_amount})

        logger.info(f'Сумма баланса в валюте {balance.currency} обновлена')
        return balance


class DeleteBalanceService:
    """Сервис по удалению балансов"""

    def __init__(self, balance_commands: 'BalanceCommandsRepository', balance_queries: 'BalanceQueriesRepository') -> None:
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries

    @debug_log
    async def delete_balance_by_id(self, balance_id: UUID) -> None:
        obj = await self._balance_queries.select_balance_by_id(balance_id)

        BalanceGuards.require_balance_exist(obj)

        await self._balance_commands.delete_balance(obj)

        logger.info(f'Баланс {balance_id} удален')


class ShowBalanceService:
    """Сервис по показу данных балансов"""

    def __init__(self, wallet_queries: 'WalletQueriesRepository', balance_queries: 'BalanceQueriesRepository') -> None:
        self._wallet_queries = wallet_queries
        self._balance_queries = balance_queries

    @debug_log
    async def show_balances(self, offset: int = 0, limit: int = 100) -> list['FullBalanceInfoDTO']:
        objs = await self._balance_queries.select_balances(offset, limit)
        return [FullBalanceInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_balance_by_id(self, balance_id: UUID) -> 'FullBalanceInfoDTO':
        obj = await self._balance_queries.select_balance_by_id(balance_id)

        BalanceGuards.require_balance_exist(obj)

        return FullBalanceInfoDTO.model_validate(obj)

    @debug_log
    async def show_balances_by_wallet_id(self, wallet_id: UUID) -> list['FullBalanceInfoDTO']:
        objs = await self._balance_queries.select_balances_by_wallet_id(wallet_id)

        return [FullBalanceInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_balances_by_wallet(self, address: str, pin: str) -> list['SecurityBalanceInfoDTO']:
        obj: 'WalletModel' = await self._wallet_queries.select_wallet_by_address(address)

        WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_verify_pin(pin, obj.pin_hash)

        balances = await self._balance_queries.select_balances_by_wallet_id(obj.wallet_id)

        return [SecurityBalanceInfoDTO.model_validate(balance) for balance in balances]
