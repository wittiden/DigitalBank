from decimal import Decimal
from typing import TYPE_CHECKING

from app.common.decorators import debug_log
from app.common.enums.transaction_enums import TransactionStatusesEnum
from app.modules.balances.exceptions import BalanceAmountIsLowerError, BalanceNotFoundError
from app.modules.balances.service.guards import BalanceGuards
from app.modules.operations.contracts.dtos import DepositDraftDTO, TransferDraftDTO, WithdrawDraftDTO
from app.modules.wallets.service.guards import WalletGuards

if TYPE_CHECKING:
    from app.database.models import BalanceModel, TransactionModel, WalletModel
    from app.modules.balances.repository.commands import BalanceCommandsRepository
    from app.modules.balances.repository.queries import BalanceQueriesRepository
    from app.modules.transactions.service.use_cases import CreateTrnService, UpdateTrnService
    from app.modules.wallets.repository.queries import WalletQueriesRepository


class DepositBalanceService:
    """Сервис по пополнению баланса"""

    def __init__(
        self,
        wallet_queries: 'WalletQueriesRepository',
        balance_commands: 'BalanceCommandsRepository',
        balance_queries: 'BalanceQueriesRepository',
        create_service: 'CreateTrnService',
        update_service: 'UpdateTrnService',
    ) -> None:
        self._wallet_queries = wallet_queries
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries
        self._create_service = create_service
        self._update_service = update_service

    @debug_log
    async def deposit_balance(self, address: str, pin: str, amount: Decimal, currency: str) -> 'DepositDraftDTO':
        fee = Decimal('1')

        wallet = await self._wallet_queries.select_wallet_by_address(address)
        wallet = WalletGuards.require_wallet_exists(wallet)
        WalletGuards.require_verify_pin(pin, wallet.pin_hash)
        WalletGuards.require_wallet_not_blocked(wallet)

        balances = await self._balance_queries.select_balances_by_wallet_id(wallet.wallet_id)

        for balance in balances:
            if balance.currency == currency:
                BalanceGuards.require_balance_not_frozen(balance)

                trn = await self._create_service.create_deposit_trn(address, amount, fee, currency)
                await self._update_service.update_trn_status(trn.transaction_id, TransactionStatusesEnum.PENDING)

                try:
                    balance.amount += amount * fee
                    await self._balance_commands.partial_update_balance(balance, {'amount': balance.amount})

                    await self._update_service.update_trn_status(trn.transaction_id, TransactionStatusesEnum.SUCCESS)
                    await self._update_service.add_trn_complete_at(trn.transaction_id)

                    return DepositDraftDTO.model_validate(trn)

                except Exception:
                    await self._update_service.update_trn_status(trn.transaction_id, TransactionStatusesEnum.FAILED)
                    await self._update_service.add_trn_complete_at(trn.transaction_id)
                    raise

        raise BalanceNotFoundError('Balance not found error')


class TransferBalanceService:
    """Сервис по переводу денег"""

    def __init__(
        self,
        wallet_queries: 'WalletQueriesRepository',
        balance_commands: 'BalanceCommandsRepository',
        balance_queries: 'BalanceQueriesRepository',
        create_service: 'CreateTrnService',
        update_service: 'UpdateTrnService',
    ) -> None:
        self._wallet_queries = wallet_queries
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries
        self._create_service = create_service
        self._update_service = update_service

    @debug_log
    async def transfer_balance(self, from_address: str, pin: str, amount: Decimal, currency: str, to_address: str) -> 'TransferDraftDTO':
        fee = Decimal('1')

        wallet = await self._wallet_queries.select_wallet_by_address(from_address)
        wallet = WalletGuards.require_wallet_exists(wallet)
        WalletGuards.require_verify_pin(pin, wallet.pin_hash)
        WalletGuards.require_wallet_not_blocked(wallet)

        to_wallet = await self._wallet_queries.select_wallet_by_address(to_address)
        to_wallet = WalletGuards.require_wallet_exists(to_wallet)
        WalletGuards.require_wallet_not_blocked(to_wallet)

        balances: list[BalanceModel] = await self._balance_queries.select_balances_by_wallet_id(wallet.wallet_id)

        to_balances: list[BalanceModel] = await self._balance_queries.select_balances_by_wallet_id(to_wallet.wallet_id)

        for balance in balances:
            if balance.currency == currency:
                BalanceGuards.require_balance_not_frozen(balance)

                for to_balance in to_balances:
                    if to_balance.currency == currency:
                        BalanceGuards.require_balance_not_frozen(to_balance)

                        trn: TransactionModel = await self._create_service.create_transfer_trn(from_address, to_address, amount, fee, currency)
                        self._update_service.update_trn_status(trn.transaction_id, TransactionStatusesEnum.PENDING)

                        try:
                            if not balance.amount >= amount * fee:
                                raise BalanceAmountIsLowerError(f'Balance amount lower than {amount * fee}')

                            balance.amount -= amount
                            await self._balance_commands.partial_update_balance(balance, {'amount': balance.amount})

                            to_balance.amount += amount * fee
                            await self._balance_commands.partial_update_balance(to_balance, {'amount': to_balance.amount})

                            await self._update_service.update_trn_status(trn.transaction_id, TransactionStatusesEnum.SUCCESS)
                            await self._update_service.add_trn_complete_at(trn.transaction_id)

                            return TransferDraftDTO.model_validate(trn)

                        except Exception:
                            await self._update_service.update_trn_status(trn.transaction_id, TransactionStatusesEnum.FAILED)
                            await self._update_service.add_trn_complete_at(trn.transaction_id)
                            raise

        raise BalanceNotFoundError('Balance not found error')


class WithdrawBalanceService:
    """Сервис по снятию денег с баланса"""

    def __init__(
        self,
        wallet_queries: 'WalletQueriesRepository',
        balance_commands: 'BalanceCommandsRepository',
        balance_queries: 'BalanceQueriesRepository',
        create_service: 'CreateTrnService',
        update_service: 'UpdateTrnService',
    ) -> None:
        self._wallet_queries = wallet_queries
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries
        self._create_service = create_service
        self._update_service = update_service

    @debug_log
    async def withdraw_balance(self, address: str, pin: str, amount: Decimal, currency: str) -> 'WithdrawDraftDTO':
        fee = Decimal('1')

        wallet = await self._wallet_queries.select_wallet_by_address(address)
        wallet = WalletGuards.require_wallet_exists(wallet)
        WalletGuards.require_verify_pin(pin, wallet.pin_hash)
        WalletGuards.require_wallet_not_blocked(wallet)

        balances = await self._balance_queries.select_balances_by_wallet_id(wallet.wallet_id)

        for balance in balances:
            if balance.currency == currency:
                BalanceGuards.require_balance_not_frozen(balance)

                trn = await self._create_service.create_withdraw_trn(address, amount, fee, currency)
                await self._update_service.update_trn_status(trn.transaction_id, TransactionStatusesEnum.PENDING)

                try:
                    if not balance.amount >= amount * fee:
                        raise BalanceAmountIsLowerError(f'Balance amount lower than {amount * fee}')

                    balance.amount -= amount * fee
                    await self._balance_commands.partial_update_balance(balance, {'amount': balance.amount})

                    await self._update_service.update_trn_status(trn.transaction_id, TransactionStatusesEnum.SUCCESS)
                    await self._update_service.add_trn_complete_at(trn.transaction_id)

                    return WithdrawDraftDTO.model_validate(trn)

                except Exception:
                    await self._update_service.update_trn_status(trn.transaction_id, TransactionStatusesEnum.FAILED)
                    await self._update_service.add_trn_complete_at(trn.transaction_id)
                    raise

        raise BalanceNotFoundError('Balance not found error')


class ExchangeBalanceService:
    """Сервис по обмену валют на или между балансами"""

    def __init__(
        self,
        wallet_queries: 'WalletQueriesRepository',
        balance_commands: 'BalanceCommandsRepository',
        balance_queries: 'BalanceQueriesRepository',
        create_service: 'CreateTrnService',
        update_service: 'UpdateTrnService',
    ) -> None:
        self._wallet_queries = wallet_queries
        self._balance_commands = balance_commands
        self._balance_queries = balance_queries
        self._create_service = create_service
        self._update_service = update_service

    # async def exchange_balance(self, address: str, pin: str, amount: Decimal, from_currency: str, to_currency: str) -> 'ExchangeDraftDTO':
    #     fee = Decimal('1')
    #     rate = Decimal('1')
    #
    #     wallet: 'WalletModel' = await self._wallet_queries.select_wallet_by_address(address)
    #     WalletGuards.require_wallet_exists(wallet)
    #     WalletGuards.require_verify_pin(pin, wallet.pin_hash)
    #
    #     balances = await self._balance_queries.select_balances_by_wallet_id(wallet.wallet_id)
    #
    #     for balance in balances:
    #         if balance.currency == from_currency:
    #             BalanceGuards.require_balance_not_frozen(balance)
    #
    #             balance.amount -= amount*fee
    #             break
    #
    #     else:
    #         raise BalanceCurrencyNotFoundError('Balance currency not found error')
    #
    #     for balance in balances:
    #         if balance.currency == to_currency:
    #             BalanceGuards.require_balance_not_frozen(balance)
    #
    #             balance.amount += amount
