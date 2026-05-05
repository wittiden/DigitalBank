from uuid import UUID
from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from app.modules.users.contracts.schemas import UpdateUserSchema
from app.modules.users.service.use_cases import UpdateUserService
from app.modules.wallets.contracts.responses import FullWalletInfoResponse, SecurityWalletInfoResponse
from app.modules.wallets.contracts.schemas import CreateWalletSchema, CloseWalletSchema, ShowWalletByAddressSchema
from app.modules.wallets.service.use_cases import CreateWalletService, DeleteWalletService, ManageWalletService, \
    ShowWalletService

user_wallet_router = APIRouter(prefix='/api/wallets', tags=['users', 'wallets'])
admin_wallet_router = APIRouter(prefix='/api/wallets', tags=['admin', 'wallets'])


@user_wallet_router.post('/create_credit_wallet', response_model=SecurityWalletInfoResponse, tags=['create'], summary='Create credit wallet')
@inject
async def create_credit_wallet_endpoint(schema: CreateWalletSchema, service: FromDishka[CreateWalletService]):
    return await service.create_credit_wallet(schema.pin, schema.email, schema.password)


@user_wallet_router.post('/create_debit_wallet', response_model=SecurityWalletInfoResponse, tags=['create'], summary='Create debit wallet')
@inject
async def create_debit_wallet_endpoint(schema: CreateWalletSchema, service: FromDishka[CreateWalletService]):
    return await service.create_debit_wallet(schema.pin, schema.email, schema.password)


@user_wallet_router.patch('/update_wallet', response_model=SecurityWalletInfoResponse, tags=['update'], summary='Update wallet')
@inject
async def partial_update_wallet_endpoint(schema: UpdateUserSchema, service: FromDishka[UpdateUserService]):
    return await service.partial_update_user(schema.email, schema.password, schema.data)


@admin_wallet_router.delete('/delete_wallet/{wallet_id}', tags=['delete'], summary='Delete wallet')
@inject
async def delete_wallet_endpoint(wallet_id: UUID, service: FromDishka[DeleteWalletService]):
    await service.delete_wallet(wallet_id)
    return {'Success': True}


@user_wallet_router.delete('/close_wallet', tags=['delete'], summary='Close wallet')
@inject
async def close_wallet_endpoint(schema: CloseWalletSchema, service: FromDishka[DeleteWalletService]):
    await service.close_wallet(schema.address, schema.pin)
    return {'Success': True}


@admin_wallet_router.patch('/block_wallet/{wallet_id}', tags=['manage'], summary='Block wallet')
@inject
async def block_wallet_endpoint(wallet_id: UUID, service: FromDishka[ManageWalletService]):
    await service.block_wallet(wallet_id)
    return {'Success': True}


@admin_wallet_router.patch('/unblock_wallet/{wallet_id}', tags=['manage'], summary='Unblock wallet')
@inject
async def unblock_wallet_endpoint(wallet_id: UUID, service: FromDishka[ManageWalletService]):
    await service.unblock_wallet(wallet_id)
    return {'Success': True}


@admin_wallet_router.get('/get_wallet/{wallet_id}', response_model=FullWalletInfoResponse, tags=['get'], summary='Show wallet by id')
@inject
async def show_wallet_by_id_endpoint(wallet_id: UUID, service: FromDishka[ShowWalletService]):
    return await service.show_wallet_by_id(wallet_id)


@admin_wallet_router.get('/get_wallets', response_model=list[FullWalletInfoResponse], tags=['get'], summary='Show wallets')
@inject
async def show_wallets_endpoint(service: FromDishka[ShowWalletService], offset: int = 0, limit: int = 100):
    return await service.show_wallets(offset, limit)


@user_wallet_router.get('/get_wallets/{user_id}', response_model=list[SecurityWalletInfoResponse], tags=['get'], summary='Show wallets by user id')
@inject
async def show_wallets_by_user_id_endpoint(user_id: UUID, service: FromDishka[ShowWalletService]):
    return await service.show_wallets_by_user_id(user_id)


@user_wallet_router.get('/get_wallet', response_model=SecurityWalletInfoResponse, tags=['get'], summary='Show wallet by address')
@inject
async def show_wallet_by_address(schema: ShowWalletByAddressSchema, service: FromDishka[ShowWalletService]):
    return await service.show_wallet_by_address(schema.address, schema.pin)
