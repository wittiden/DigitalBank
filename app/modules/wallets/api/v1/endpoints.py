from uuid import UUID
from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from app.api.v1.endpoints import CurrentUser, CurrentAdmin
from app.unit_of_work.uow import UnitOfWork
from app.modules.wallets.contracts.responses import FullWalletInfoResponse, SecurityWalletInfoResponse
from app.modules.wallets.contracts.schemas import CreateWalletSchema, CloseWalletSchema, UpdateWalletSchema, \
    UpdateParamsWalletSchema
from app.modules.wallets.service.use_cases import CreateWalletService, DeleteWalletService, ManageWalletService, \
    ShowWalletService, UpdateWalletService

user_wallet_router = APIRouter(prefix='/api/v1/wallets', tags=['wallets'])
admin_wallet_router = APIRouter(prefix='/api/v1/admin/wallets', tags=['wallets'])


@user_wallet_router.post('/credit', response_model=SecurityWalletInfoResponse, summary='Create credit wallet')
@inject
async def create_credit_wallet_endpoint(current_user: CurrentUser, schema: CreateWalletSchema, service: FromDishka[CreateWalletService], uow: FromDishka[UnitOfWork]) -> SecurityWalletInfoResponse:
    return await service.create_credit_wallet(current_user, schema.pin)


@user_wallet_router.post('/debit', response_model=SecurityWalletInfoResponse, summary='Create debit wallet')
@inject
async def create_debit_wallet_endpoint(current_user: CurrentUser, schema: CreateWalletSchema, service: FromDishka[CreateWalletService], uow: FromDishka[UnitOfWork]) -> SecurityWalletInfoResponse:
    return await service.create_debit_wallet(current_user, schema.pin)


@user_wallet_router.patch('/', response_model=SecurityWalletInfoResponse, summary='Update wallet')
@inject
async def update_my_wallet_endpoint(current_user: CurrentUser, schema: UpdateWalletSchema, params_schema: UpdateParamsWalletSchema, service: FromDishka[UpdateWalletService], uow: FromDishka[UnitOfWork]) -> SecurityWalletInfoResponse:
    return await service.partial_update_my_wallet(current_user, schema.address, schema.pin, params_schema.model_dump(exclude_none=True))


@admin_wallet_router.delete('/{wallet_id}', summary='Delete wallet')
@inject
async def delete_wallet_endpoint(current_user: CurrentAdmin, wallet_id: UUID, service: FromDishka[DeleteWalletService], uow: FromDishka[UnitOfWork]) -> None:
    await service.delete_wallet(current_user, wallet_id)


@user_wallet_router.delete('/me', summary='Close my wallet')
@inject
async def close_my_wallet_endpoint(current_user: CurrentUser, schema: CloseWalletSchema, service: FromDishka[DeleteWalletService], uow: FromDishka[UnitOfWork]) -> None:
    await service.close_my_wallet(current_user, schema.address, schema.pin)


@admin_wallet_router.patch('/block/{wallet_id}', summary='Block wallet')
@inject
async def block_wallet_endpoint(current_user: CurrentAdmin, wallet_id: UUID, service: FromDishka[ManageWalletService], uow: FromDishka[UnitOfWork]) -> None:
    await service.block_wallet(current_user, wallet_id)


@admin_wallet_router.patch('/unblock/{wallet_id}', summary='Unblock wallet')
@inject
async def unblock_wallet_endpoint(current_user: CurrentAdmin, wallet_id: UUID, service: FromDishka[ManageWalletService], uow: FromDishka[UnitOfWork]) -> None:
    await service.unblock_wallet(current_user, wallet_id)


@admin_wallet_router.get('/{wallet_id}', response_model=FullWalletInfoResponse, summary='Get wallet by id')
@inject
async def get_wallet_by_id_endpoint(current_user: CurrentAdmin, wallet_id: UUID, service: FromDishka[ShowWalletService], uow: FromDishka[UnitOfWork]) -> FullWalletInfoResponse:
    return await service.show_wallet_by_id(current_user, wallet_id)


@admin_wallet_router.get('/by_user_id/{user_id}', response_model=list[FullWalletInfoResponse], summary='Get wallets by user id')
@inject
async def get_wallets_by_user_id_endpoint(current_user: CurrentAdmin, user_id: UUID, service: FromDishka[ShowWalletService], uow: FromDishka[UnitOfWork]) -> list[FullWalletInfoResponse]:
    return await service.show_wallets_by_user_id(current_user, user_id)


@admin_wallet_router.get('/', response_model=list[FullWalletInfoResponse], summary='Get wallets')
@inject
async def get_wallets_endpoint(current_user: CurrentAdmin, service: FromDishka[ShowWalletService], uow: FromDishka[UnitOfWork], offset: int = 0, limit: int = 100) -> list[FullWalletInfoResponse]:
    return await service.show_wallets(current_user, offset, limit)


@user_wallet_router.get('/me', response_model=list[SecurityWalletInfoResponse], summary='Get my wallets')
@inject
async def get_my_wallets_endpoint(current_user: CurrentUser, service: FromDishka[ShowWalletService], uow: FromDishka[UnitOfWork]) -> list[SecurityWalletInfoResponse]:
    return await service.show_my_wallets(current_user)
