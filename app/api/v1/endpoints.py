from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from app.common.uow import UnitOfWork
from app.modules.transactions.contracts.schemas import DepositSchema, WithdrawSchema, TransferSchema, ExchangeSchema
from app.modules.balances.service.operation_use_cases import DepositBalanceService, TransferBalanceService, \
    WithdrawBalanceService
from app.modules.transactions.contracts.responses import DepositDraftResponse, TransferDraftResponse, \
    WithdrawDraftResponse

operation_router = APIRouter(prefix='/api/operations', tags=['operations'])


@operation_router.post('/deposit', response_model=DepositDraftResponse, summary='Deposit balance')
@inject
async def deposit_balance(schema: DepositSchema, service: FromDishka[DepositBalanceService], uow: FromDishka[UnitOfWork]) -> DepositDraftResponse:
    return await service.deposit_balance(schema.address, schema.pin, schema.amount, schema.currency)


@operation_router.post('/transfer', response_model=TransferDraftResponse, summary='Transfer balance')
@inject
async def transfer_balance(schema: TransferSchema, service: FromDishka[TransferBalanceService], uow: FromDishka[UnitOfWork]) -> TransferDraftResponse:
    return await service.transfer_balance(schema.from_address, schema.pin, schema.amount, schema.currency, schema.to_address)


@operation_router.post('/withdraw', response_model=WithdrawDraftResponse, summary='Withdraw balance')
@inject
async def withdraw_balance(schema: WithdrawSchema, service: FromDishka[WithdrawBalanceService], uow: FromDishka[UnitOfWork]) -> WithdrawDraftResponse:
    return await service.withdraw_balance(schema.address, schema.pin, schema.amount, schema.currency)
