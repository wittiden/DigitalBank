from datetime import datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from loguru import logger
from typing import TYPE_CHECKING

from app.common.decorators import debug_log
from app.common.enums.transaction_enums import TransactionTypesEnum
from app.modules.transactions.contracts.dtos import FullTrnInfoDTO
from app.modules.transactions.exceptions import TrnNotFoundError, TrnCreateError, TrnCurrenciesIsTheSameError

if TYPE_CHECKING:
    from app.modules.transactions.uow.uow import TrnUnitOfWork


class CreateTrnService:
    """Сервис по созданию транзакций"""

    def __init__(self, trn_uow: 'TrnUnitOfWork') -> None:
        self._trn_uow = trn_uow

    async def _create_trn(self, from_wallet_id: UUID, amount: Decimal, fee: Decimal, started_at: datetime, transaction_type: 'TransactionTypesEnum', to_wallet_id: UUID,  rate: Decimal = None, from_currency: str = None, to_currency: str = None) -> 'FullTrnInfoDTO':
        try:
            obj = await self._trn_uow.trn_commands.insert_trn_info(from_wallet_id=from_wallet_id, amount=amount, fee=fee, started_at=started_at, from_currency=from_currency, transaction_type=transaction_type, to_wallet_id=to_wallet_id, rate=rate, to_currency=to_currency)
        except IntegrityError:
            await self._trn_uow.rollback()
            raise TrnCreateError('Error while transaction created')

        await self._trn_uow.commit()
        logger.info('Create transaction')

        return FullTrnInfoDTO.model_validate(obj)

    @debug_log
    async def create_deposit_trn(self, from_wallet_id: UUID, amount: Decimal, fee: Decimal, from_currency: str, to_wallet_id: UUID) -> 'FullTrnInfoDTO':
        trn = await self._create_trn(from_wallet_id=from_wallet_id, amount=amount, fee=fee, started_at=datetime.now(), transaction_type=TransactionTypesEnum.DEPOSIT, to_wallet_id=to_wallet_id, from_currency=from_currency)
        return FullTrnInfoDTO.model_validate(trn)

    @debug_log
    async def create_withdraw_trn(self, from_wallet_id: UUID, amount: Decimal, fee: Decimal, from_currency: str, to_wallet_id: UUID) -> 'FullTrnInfoDTO':
        trn = await self._create_trn(from_wallet_id=from_wallet_id, amount=amount, fee=fee, started_at=datetime.now(), transaction_type=TransactionTypesEnum.WITHDRAW, from_currency=from_currency, to_wallet_id=to_wallet_id)
        return FullTrnInfoDTO.model_validate(trn)

    @debug_log
    async def create_exchange_trn(self, from_wallet_id: UUID, amount: Decimal, fee: Decimal, rate: Decimal, from_currency: str, to_currency: str, to_wallet_id: UUID) -> 'FullTrnInfoDTO':
        trn = await self._create_trn(from_wallet_id=from_wallet_id, amount=amount, fee=fee, started_at=datetime.now(), transaction_type=TransactionTypesEnum.EXCHANGE, to_wallet_id=to_wallet_id, rate=rate, from_currency=from_currency, to_currency=to_currency)

        if from_currency == to_currency:
            raise TrnCurrenciesIsTheSameError(f'Transaction currencies is the same ({from_currency} != {to_currency})')

        return FullTrnInfoDTO.model_validate(trn)


class ShowTrnService:
    """Сервис по показу информации о транзакциях"""

    def __init__(self, trn_uow: 'TrnUnitOfWork') -> None:
        self._trn_uow = trn_uow

    @debug_log
    async def show_trns(self, offset: int = 0, limit: int = 0) -> list['FullTrnInfoDTO']:
        objs = await self._trn_uow.trn_queries.select_trns(offset, limit)
        return [FullTrnInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_trn_by_id(self, trn_id: UUID) -> 'FullTrnInfoDTO':
        obj = await self._trn_uow.trn_queries.select_trn_by_id(trn_id)

        if not obj:
            raise TrnNotFoundError('Transaction not found')

        return FullTrnInfoDTO.model_validate(obj)
