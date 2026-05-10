from uuid import UUID
from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from app.unit_of_work.uow import UnitOfWork
from app.modules.wallets.contracts.responses import FullWalletInfoResponse, SecurityWalletInfoResponse
from app.modules.wallets.contracts.schemas import CreateWalletSchema, CloseWalletSchema, \
    UpdateWalletSchema, UpdateWalletUserSchema
from app.modules.wallets.service.use_cases import CreateWalletService, DeleteWalletService, ManageWalletService, \
    ShowWalletService, UpdateWalletService

user_wallet_router = APIRouter(prefix='/api/v1/wallets', tags=['users', 'wallets'])
admin_wallet_router = APIRouter(prefix='/api/v1/admin/wallets', tags=['admin', 'wallets'])


@user_wallet_router.post('/credit', response_model=SecurityWalletInfoResponse, summary='Create credit wallet')
@inject
async def create_credit_wallet_endpoint(schema: CreateWalletSchema, service: FromDishka[CreateWalletService], uow: FromDishka[UnitOfWork]) -> SecurityWalletInfoResponse:
    return await service.create_credit_wallet(schema.pin, schema.email, schema.password)


@user_wallet_router.post('/debit', response_model=SecurityWalletInfoResponse, summary='Create debit wallet')
@inject
async def create_debit_wallet_endpoint(schema: CreateWalletSchema, service: FromDishka[CreateWalletService], uow: FromDishka[UnitOfWork]) -> SecurityWalletInfoResponse:
    return await service.create_debit_wallet(schema.pin, schema.email, schema.password)


@user_wallet_router.patch('/', response_model=SecurityWalletInfoResponse, summary='Update wallet')
@inject
async def update_wallet_endpoint(schema: UpdateWalletSchema, service: FromDishka[UpdateWalletService], uow: FromDishka[UnitOfWork]) -> SecurityWalletInfoResponse:
    return await service.partial_update_wallet(schema.address, schema.pin, schema.data)


@admin_wallet_router.patch('/', response_model=FullWalletInfoResponse, summary='Update wallet user')
@inject
async def update_wallet_user_endpoint(schema: UpdateWalletUserSchema, service: FromDishka[UpdateWalletService], uow: FromDishka[UnitOfWork]) -> FullWalletInfoResponse:
    return await service.update_wallet_user(schema.address, schema.pin, schema.old_email, schema.old_password, schema.new_email, schema.new_password)


@admin_wallet_router.delete('/{wallet_id}', summary='Delete wallet')
@inject
async def delete_wallet_endpoint(wallet_id: UUID, service: FromDishka[DeleteWalletService], uow: FromDishka[UnitOfWork]) -> None:
    await service.delete_wallet(wallet_id)


@user_wallet_router.delete('/', summary='Close wallet')
@inject
async def close_wallet_endpoint(schema: CloseWalletSchema, service: FromDishka[DeleteWalletService], uow: FromDishka[UnitOfWork]) -> None:
    await service.close_wallet(schema.address, schema.pin)


@admin_wallet_router.patch('/block/{wallet_id}', summary='Block wallet')
@inject
async def block_wallet_endpoint(wallet_id: UUID, service: FromDishka[ManageWalletService], uow: FromDishka[UnitOfWork]) -> None:
    await service.block_wallet(wallet_id)


@admin_wallet_router.patch('/unblock/{wallet_id}', summary='Unblock wallet')
@inject
async def unblock_wallet_endpoint(wallet_id: UUID, service: FromDishka[ManageWalletService], uow: FromDishka[UnitOfWork]) -> None:
    await service.unblock_wallet(wallet_id)


@admin_wallet_router.get('/{wallet_id}', response_model=FullWalletInfoResponse, summary='Get wallet by id')
@inject
async def get_wallet_by_id_endpoint(wallet_id: UUID, service: FromDishka[ShowWalletService], uow: FromDishka[UnitOfWork]) -> FullWalletInfoResponse:
    return await service.show_wallet_by_id(wallet_id)


@admin_wallet_router.get('/by_user/{user_id}', response_model=list[FullWalletInfoResponse], summary='Get wallets by user id')
@inject
async def get_wallets_by_user_id_endpoint(user_id: UUID, service: FromDishka[ShowWalletService], uow: FromDishka[UnitOfWork]) -> list[FullWalletInfoResponse]:
    return await service.show_wallets_by_user_id(user_id)


@admin_wallet_router.get('/', response_model=list[FullWalletInfoResponse], summary='Get wallets')
@inject
async def get_wallets_endpoint(service: FromDishka[ShowWalletService], uow: FromDishka[UnitOfWork], offset: int = 0, limit: int = 100) -> list[FullWalletInfoResponse]:
    return await service.show_wallets(offset, limit)


# @user_wallet_router.get('/my_wallets', response_model=list[SecurityWalletInfoResponse], summary='Get my wallets')
# @inject
# async def get_my_wallets_endpoint(schema: ShowMyWalletsSchema, service: FromDishka[ShowWalletService], uow: FromDishka[UnitOfWork]) -> list[SecurityWalletInfoResponse]:
#     return await service.show_my_wallets(schema.email, schema.password)
