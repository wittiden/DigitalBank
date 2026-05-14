from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.common.decorators import debug_log
from app.common.enums.balance_enums import BalanceTypesEnum
from app.modules.balances.contracts.dtos import FullBalanceInfoDTO, SecurityBalanceInfoDTO
from app.modules.balances.exceptions import BalanceAmountIsNotZeroError, BalanceCurrencyNotFoundError, CreateBalanceError
from app.modules.balances.service.guards import BalanceGuards
from app.modules.users.service.guards import UserGuards
from app.modules.wallets.service.guards import WalletGuards

if TYPE_CHECKING:
    from app.database.models import UserModel
    from app.modules.balances.repository.commands import BalanceCommandsRepository
    from app.modules.balances.repository.queries import BalanceQueriesRepository
    from app.modules.wallets.repository.queries import WalletQueriesRepository


class CreateBalanceService:
    """Сервис по созданию балансов"""

    def __init__(self, wallet_queries: 'WalletQueriesRepository', balance_commands: 'BalanceCommandsRepository', balance_queries: 'BalanceQueriesRepository') -> None:
        self._wallet_queries = wallet_queries
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries

    async def _create_balance(self, current_user: 'UserModel', address: str, pin: str, currency: str, amount: Decimal, balance_type: BalanceTypesEnum) -> 'SecurityBalanceInfoDTO':
        UserGuards.require_user_exists(current_user)

        obj = await self._wallet_queries.select_wallet_by_address(address)

        obj = WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_verify_pin(pin, obj.pin_hash)
        WalletGuards.require_wallet_not_blocked(obj)

        try:
            balance = await self._balance_commands.insert_balance_info(currency, amount, balance_type, obj.wallet_id)
        except IntegrityError as err:
            raise CreateBalanceError('Create balance error') from err

        balance_count = await self._balance_queries.select_balances_count(balance.wallet_id)
        BalanceGuards.require_balance_limit(balance_count)

        logger.info(f'Баланс привязанный к адресу {address} создан')
        return SecurityBalanceInfoDTO.model_validate(balance)

    @debug_log
    async def create_regular_balance(self, current_user: 'UserModel', address: str, pin: str, currency: str, amount: Decimal) -> 'SecurityBalanceInfoDTO':
        return await self._create_balance(current_user, address, pin, currency, amount, BalanceTypesEnum.REGULAR)

    @debug_log
    async def create_foreign_balance(self, current_user: 'UserModel', address: str, pin: str, currency: str, amount: Decimal) -> 'SecurityBalanceInfoDTO':
        return await self._create_balance(current_user, address, pin, currency, amount, BalanceTypesEnum.FOREIGN)


class ManageBalanceService:
    """Сервис по менедженгу балансов"""

    def __init__(self, balance_commands: 'BalanceCommandsRepository', balance_queries: 'BalanceQueriesRepository') -> None:
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries

    @debug_log
    async def freeze_balance(self, current_user: 'UserModel', balance_id: UUID) -> None:
        UserGuards.require_admin(current_user)

        obj = await self._balance_queries.select_balance_by_id(balance_id)

        obj = BalanceGuards.require_balance_exist(obj)
        BalanceGuards.require_balance_not_frozen(obj)

        await self._balance_commands.partial_update_balance(obj, {'is_frozen': True})

        logger.info(f'Баланс #{balance_id} заморожен')

    @debug_log
    async def unfreeze_balance(self, current_user: 'UserModel', balance_id: UUID) -> None:
        UserGuards.require_admin(current_user)

        obj = await self._balance_queries.select_balance_by_id(balance_id)

        obj = BalanceGuards.require_balance_exist(obj)
        BalanceGuards.require_balance_not_unfrozen(obj)

        await self._balance_commands.partial_update_balance(obj, {'is_frozen': False})

        logger.info(f'Баланс #{balance_id} разморожен')


class DeleteBalanceService:
    """Сервис по удалению балансов"""

    def __init__(self, balance_commands: 'BalanceCommandsRepository', balance_queries: 'BalanceQueriesRepository', wallet_queries: 'WalletQueriesRepository') -> None:
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries
        self._wallet_queries = wallet_queries

    @debug_log
    async def delete_balance_by_id(self, current_user: 'UserModel', balance_id: UUID) -> None:
        UserGuards.require_admin(current_user)

        obj = await self._balance_queries.select_balance_by_id(balance_id)

        obj = BalanceGuards.require_balance_exist(obj)

        await self._balance_commands.delete_balance(obj)

        logger.info(f'Баланс {balance_id} удален')

    @debug_log
    async def close_balance(self, current_user: 'UserModel', address: str, pin: str, currency: str) -> None:
        UserGuards.require_user_exists(current_user)

        wallet = await self._wallet_queries.select_wallet_by_address(address)

        wallet = WalletGuards.require_wallet_exists(wallet)
        WalletGuards.require_verify_pin(pin, wallet.pin_hash)
        WalletGuards.require_wallet_not_blocked(wallet)

        balances = await self._balance_queries.select_balances_by_wallet_id(wallet.wallet_id)

        for balance in balances:
            if balance.currency == currency:
                if balance.amount != 0:
                    raise BalanceAmountIsNotZeroError('Balance amount is not zero error')

                await self._balance_commands.delete_balance(balance)

        else:
            raise BalanceCurrencyNotFoundError('Balance currency not found error')


class ShowBalanceService:
    """Сервис по показу данных балансов"""

    def __init__(self, wallet_queries: 'WalletQueriesRepository', balance_queries: 'BalanceQueriesRepository') -> None:
        self._wallet_queries = wallet_queries
        self._balance_queries = balance_queries

    @debug_log
    async def show_balances(self, current_user: 'UserModel', offset: int = 0, limit: int = 100) -> list['FullBalanceInfoDTO']:
        UserGuards.require_admin(current_user)

        objs = await self._balance_queries.select_balances(offset, limit)

        return [FullBalanceInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_balance_by_id(self, current_user: 'UserModel', balance_id: UUID) -> 'FullBalanceInfoDTO':
        UserGuards.require_admin(current_user)

        obj = await self._balance_queries.select_balance_by_id(balance_id)

        BalanceGuards.require_balance_exist(obj)

        return FullBalanceInfoDTO.model_validate(obj)

    @debug_log
    async def show_balances_by_wallet_id(self, current_user: 'UserModel', wallet_id: UUID) -> list['FullBalanceInfoDTO']:
        UserGuards.require_admin(current_user)

        objs = await self._balance_queries.select_balances_by_wallet_id(wallet_id)

        return [FullBalanceInfoDTO.model_validate(obj) for obj in objs]

    # @debug_log
    # async def show_balances_by_wallet(self, address: str, pin: str) -> list['SecurityBalanceInfoDTO']:
    #     obj: 'WalletModel' = await self._wallet_queries.select_wallet_by_address(address)
    #
    #     WalletGuards.require_wallet_exists(obj)
    #     WalletGuards.require_verify_pin(pin, obj.pin_hash)
    #
    #     balances = await self._balance_queries.select_balances_by_wallet_id(obj.wallet_id)
    #
    #     return [SecurityBalanceInfoDTO.model_validate(balance) for balance in balances]
