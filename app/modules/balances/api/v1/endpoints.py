from uuid import UUID
from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from app.common.uow import UnitOfWork
from app.modules.balances.contracts.responses import SecurityBalanceInfoResponse, FullBalanceInfoResponse
from app.modules.balances.contracts.schemas import CreateRegularBalanceSchema, CreateForeignBalanceSchema, \
    ShowBalancesByWalletSchema
from app.modules.balances.service.use_cases import CreateBalanceService, ManageBalanceService, ShowBalanceService, \
    DeleteBalanceService

user_balance_router = APIRouter(prefix='/api/v1/balances', tags=['users', 'balance'])
admin_balance_router = APIRouter(prefix='/api/v1/admin/balances', tags=['admin', 'balance'])


@user_balance_router.post('/regular', response_model=SecurityBalanceInfoResponse, summary='Create regular balance')
@inject
async def create_regular_balance_endpoint(schema: CreateRegularBalanceSchema, service: FromDishka[CreateBalanceService], uow: FromDishka[UnitOfWork]) -> SecurityBalanceInfoResponse:
    return await service.create_regular_balance(schema.currency, schema.amount, schema.address, schema.pin)


@user_balance_router.post('/foreign', response_model=SecurityBalanceInfoResponse, summary='Create foreign balance')
@inject
async def create_foreign_balance_endpoint(schema: CreateForeignBalanceSchema, service: FromDishka[CreateBalanceService], uow: FromDishka[UnitOfWork]) -> SecurityBalanceInfoResponse:
    return await service.create_foreign_balance(schema.currency, schema.amount, schema.address, schema.pin)


@admin_balance_router.patch('/freeze/{balance_id}', summary='Freeze balance')
@inject
async def freeze_balance_endpoint(balance_id: UUID, service: FromDishka[ManageBalanceService], uow: FromDishka[UnitOfWork]) -> None:
    await service.freeze_balance(balance_id)


@admin_balance_router.patch('/unfreeze/{balance_id}', summary='Unfreeze balance')
@inject
async def unfreeze_balance_endpoint(balance_id: UUID, service: FromDishka[ManageBalanceService], uow: FromDishka[UnitOfWork]) -> None:
    await service.unfreeze_balance(balance_id)


@admin_balance_router.delete('/{balance_id}', summary='Delete balance by id')
@inject
async def delete_balance_by_id_endpoint(balance_id: UUID, service: FromDishka[DeleteBalanceService], uow: FromDishka[UnitOfWork]) -> None:
    await service.delete_balance_by_id(balance_id)


@admin_balance_router.get('/', response_model=list[FullBalanceInfoResponse], summary='Get balances')
@inject
async def get_balances_endpoint(service: FromDishka[ShowBalanceService], uow: FromDishka[UnitOfWork], offset: int = 0, limit: int = 100) -> list[FullBalanceInfoResponse]:
    return await service.show_balances(offset, limit)


@admin_balance_router.get('/by_id', response_model=FullBalanceInfoResponse, summary='Get balance by id')
@inject
async def get_balance_by_id_endpoint(balance_id: UUID, service: FromDishka[ShowBalanceService], uow: FromDishka[UnitOfWork]) -> FullBalanceInfoResponse:
    return await service.show_balance_by_id(balance_id)


@admin_balance_router.get('/by_wallet_id', response_model=list[FullBalanceInfoResponse], summary='Get balances by wallet id')
@inject
async def get_balances_by_wallet_id_endpoint(wallet_id: UUID, service: FromDishka[ShowBalanceService], uow: FromDishka[UnitOfWork]) -> list[FullBalanceInfoResponse]:
    return await service.show_balances_by_wallet_id(wallet_id)
