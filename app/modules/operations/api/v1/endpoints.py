from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.modules.operations.contracts.responses import DepositDraftResponse, TransferDraftResponse, WithdrawDraftResponse
from app.modules.operations.contracts.schemas import DepositSchema, TransferSchema, WithdrawSchema
from app.modules.operations.service.use_cases import DepositBalanceService, TransferBalanceService, WithdrawBalanceService
from app.unit_of_work.uow import UnitOfWork

operation_router = APIRouter(prefix='/api/v1/operations', tags=['operations'])


@operation_router.post('/deposit', response_model=DepositDraftResponse, summary='Deposit balance')
@inject
async def deposit_balance(schema: DepositSchema, service: FromDishka[DepositBalanceService], uow: FromDishka[UnitOfWork]) -> DepositDraftResponse:
    dto = await service.deposit_balance(schema.address, schema.pin, schema.amount, schema.currency)
    return DepositDraftResponse.model_validate(dto)


@operation_router.post('/transfer', response_model=TransferDraftResponse, summary='Transfer balance')
@inject
async def transfer_balance(schema: TransferSchema, service: FromDishka[TransferBalanceService], uow: FromDishka[UnitOfWork]) -> TransferDraftResponse:
    dto = await service.transfer_balance(schema.from_address, schema.pin, schema.amount, schema.currency, schema.to_address)
    return TransferDraftResponse.model_validate(dto)


@operation_router.post('/withdraw', response_model=WithdrawDraftResponse, summary='Withdraw balance')
@inject
async def withdraw_balance(schema: WithdrawSchema, service: FromDishka[WithdrawBalanceService], uow: FromDishka[UnitOfWork]) -> WithdrawDraftResponse:
    dto = await service.withdraw_balance(schema.address, schema.pin, schema.amount, schema.currency)
    return WithdrawDraftResponse.model_validate(dto)
