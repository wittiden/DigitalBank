from uuid import UUID
from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from app.api.v1.endpoints import CurrentUser, CurrentAdmin
from app.unit_of_work.uow import UnitOfWork
from app.modules.balances.contracts.responses import SecurityBalanceInfoResponse, FullBalanceInfoResponse
from app.modules.balances.contracts.schemas import CreateBalanceSchema, CloseBalanceSchema
from app.modules.balances.service.use_cases import CreateBalanceService, ManageBalanceService, ShowBalanceService, \
    DeleteBalanceService

user_balance_router = APIRouter(prefix='/api/v1/balances', tags=['balance'])
admin_balance_router = APIRouter(prefix='/api/v1/admin/balances', tags=['balance'])


@user_balance_router.post('/regular', response_model=SecurityBalanceInfoResponse, summary='Create regular balance')
@inject
async def create_regular_balance_endpoint(current_user: CurrentUser, schema: CreateBalanceSchema, service: FromDishka[CreateBalanceService], uow: FromDishka[UnitOfWork]) -> SecurityBalanceInfoResponse:
    return await service.create_regular_balance(current_user, schema.address, schema.pin, schema.currency, schema.amount)


@user_balance_router.post('/foreign', response_model=SecurityBalanceInfoResponse, summary='Create foreign balance')
@inject
async def create_foreign_balance_endpoint(current_user: CurrentUser, schema: CreateBalanceSchema, service: FromDishka[CreateBalanceService], uow: FromDishka[UnitOfWork]) -> SecurityBalanceInfoResponse:
    return await service.create_foreign_balance(current_user, schema.address, schema.pin, schema.currency, schema.amount)


@admin_balance_router.patch('/freeze/{balance_id}', summary='Freeze balance')
@inject
async def freeze_balance_endpoint(current_user: CurrentAdmin, balance_id: UUID, service: FromDishka[ManageBalanceService], uow: FromDishka[UnitOfWork]) -> None:
    await service.freeze_balance(current_user, balance_id)


@admin_balance_router.patch('/unfreeze/{balance_id}', summary='Unfreeze balance')
@inject
async def unfreeze_balance_endpoint(current_user: CurrentAdmin, balance_id: UUID, service: FromDishka[ManageBalanceService], uow: FromDishka[UnitOfWork]) -> None:
    await service.unfreeze_balance(current_user, balance_id)


@admin_balance_router.delete('/{balance_id}', summary='Delete balance by id')
@inject
async def delete_balance_by_id_endpoint(current_user: CurrentAdmin, balance_id: UUID, service: FromDishka[DeleteBalanceService], uow: FromDishka[UnitOfWork]) -> None:
    await service.delete_balance_by_id(current_user, balance_id)


@user_balance_router.delete('/', summary='Close balance')
@inject
async def close_balance_endpoint(current_user: CurrentAdmin, schema: CloseBalanceSchema, service: FromDishka[DeleteBalanceService], uow: FromDishka[UnitOfWork]) -> None:
    await service.close_balance(current_user, schema.address, schema.pin, schema.currency)


@admin_balance_router.get('/', response_model=list[FullBalanceInfoResponse], summary='Get balances')
@inject
async def get_balances_endpoint(current_user: CurrentAdmin, service: FromDishka[ShowBalanceService], uow: FromDishka[UnitOfWork], offset: int = 0, limit: int = 100) -> list[FullBalanceInfoResponse]:
    return await service.show_balances(current_user, offset, limit)


@admin_balance_router.get('/by_id', response_model=FullBalanceInfoResponse, summary='Get balance by id')
@inject
async def get_balance_by_id_endpoint(current_user: CurrentAdmin, balance_id: UUID, service: FromDishka[ShowBalanceService], uow: FromDishka[UnitOfWork]) -> FullBalanceInfoResponse:
    return await service.show_balance_by_id(current_user, balance_id)


@admin_balance_router.get('/by_wallet_id', response_model=list[FullBalanceInfoResponse], summary='Get balances by wallet id')
@inject
async def get_balances_by_wallet_id_endpoint(current_user: CurrentAdmin, wallet_id: UUID, service: FromDishka[ShowBalanceService], uow: FromDishka[UnitOfWork]) -> list[FullBalanceInfoResponse]:
    return await service.show_balances_by_wallet_id(current_user, wallet_id)
