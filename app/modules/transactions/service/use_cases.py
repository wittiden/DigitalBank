from datetime import datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from loguru import logger
from typing import TYPE_CHECKING

from app.common.decorators import debug_log
from app.common.enums.transaction_enums import TransactionTypesEnum, TransactionStatusesEnum
from app.modules.transactions.contracts.dtos import FullTrnInfoDTO
from app.modules.transactions.exceptions import TrnCreateError, TrnCurrenciesIsTheSameError
from app.modules.transactions.service.guards import TrnGuards
from app.modules.users.service.guards import UserGuards

if TYPE_CHECKING:
    from app.database.models import UserModel
    from app.database.models import TransactionModel
    from app.modules.transactions.repository.commands import TrnCommandsRepository
    from app.modules.transactions.repository.queries import TrnQueriesRepository


class CreateTrnService:
    """Сервис по созданию транзакций"""

    def __init__(self, trn_commands: 'TrnCommandsRepository') -> None:
        self._trn_commands = trn_commands

    async def _create_trn(self, from_address: str, to_address: str, amount: Decimal, fee: Decimal, started_at: datetime, transaction_type: 'TransactionTypesEnum',  rate: Decimal = None, from_currency: str = None, to_currency: str = None) -> 'TransactionModel':
        try:
            obj = await self._trn_commands.insert_trn_info(from_address=from_address, to_address=to_address, amount=amount, fee=fee, started_at=started_at, from_currency=from_currency, transaction_type=transaction_type, rate=rate, to_currency=to_currency)
        except IntegrityError:
            raise TrnCreateError('Error while transaction created')

        logger.log(
            "TRANSACTION",
            f"Create transaction #{obj.transaction_id}, from_address={obj.from_address}, to_address={obj.to_address}, amount={obj.amount}, fee={obj.fee}, rate={obj.rate}, from_currency={obj.from_currency}, to_currency={obj.to_currency}, started_at={obj.started_at}, status={obj.transaction_status}, type={obj.transaction_type}",
        )

        return obj

    @debug_log
    async def create_deposit_trn(self, from_address: str, amount: Decimal, fee: Decimal, from_currency: str) -> 'TransactionModel':
        trn = await self._create_trn(from_address=from_address, to_address=from_address, amount=amount, fee=fee, started_at=datetime.now(), transaction_type=TransactionTypesEnum.DEPOSIT, from_currency=from_currency)
        return trn

    @debug_log
    async def create_transfer_trn(self, from_address: str, to_address: str, amount: Decimal, fee: Decimal, from_currency: str) -> 'TransactionModel':
        trn = await self._create_trn(from_address=from_address, to_address=to_address, amount=amount, fee=fee, started_at=datetime.now(), transaction_type=TransactionTypesEnum.TRANSFER, from_currency=from_currency)
        return trn

    @debug_log
    async def create_withdraw_trn(self, from_address: str, amount: Decimal, fee: Decimal, from_currency: str) -> 'TransactionModel':
        trn = await self._create_trn(from_address=from_address, to_address=from_address, amount=amount, fee=fee, started_at=datetime.now(), transaction_type=TransactionTypesEnum.WITHDRAW, from_currency=from_currency)
        return trn

    @debug_log
    async def create_exchange_trn(self, from_address: str, amount: Decimal, fee: Decimal, rate: Decimal, from_currency: str, to_currency: str) -> 'TransactionModel':
        trn = await self._create_trn(from_address=from_address, to_address=from_address, amount=amount, fee=fee, started_at=datetime.now(), transaction_type=TransactionTypesEnum.EXCHANGE, rate=rate, from_currency=from_currency, to_currency=to_currency)

        if from_currency == to_currency:
            raise TrnCurrenciesIsTheSameError(f'Transaction currencies is the same ({from_currency} != {to_currency})')

        return trn


class UpdateTrnService:
    """Сервис по обновлению данных транзакции"""

    def __init__(self, trn_commands: 'TrnCommandsRepository', trn_queries: 'TrnQueriesRepository') -> None:
        self._trn_commands = trn_commands
        self._trn_queries = trn_queries

    @debug_log
    async def update_trn_status(self, transaction_id: UUID, new_trn_status: TransactionStatusesEnum) -> 'TransactionModel':
        obj = await self._trn_queries.select_trn_by_id(transaction_id)

        TrnGuards.require_trn_exist(obj)

        await self._trn_commands.partial_update_trn(obj, {'transaction_status': new_trn_status})

        logger.log(
            "TRANSACTION",
            f"Update transaction #{obj.transaction_id}, new_status={obj.transaction_status}",
        )

        return obj

    @debug_log
    async def add_trn_complete_at(self, transaction_id: UUID) -> 'TransactionModel':
        obj = await self._trn_queries.select_trn_by_id(transaction_id)

        TrnGuards.require_trn_exist(obj)

        await self._trn_commands.partial_update_trn(obj, {'completed_at': datetime.now()})

        logger.log(
            "TRANSACTION",
            f"Update transaction #{obj.transaction_id}, completed_at={obj.completed_at}",
        )

        return obj


class ShowTrnService:
    """Сервис по показу информации о транзакциях"""

    def __init__(self, trn_queries: 'TrnQueriesRepository') -> None:
        self._trn_queries = trn_queries

    @debug_log
    async def show_trns(self, current_user: 'UserModel', offset: int = 0, limit: int = 100) -> list['FullTrnInfoDTO']:
        UserGuards.require_admin(current_user)

        objs = await self._trn_queries.select_trns(offset, limit)

        return [FullTrnInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_trn_by_id(self, current_user: 'UserModel', trn_id: UUID) -> 'FullTrnInfoDTO':
        UserGuards.require_admin(current_user)

        obj = await self._trn_queries.select_trn_by_id(trn_id)

        return FullTrnInfoDTO.model_validate(obj)
