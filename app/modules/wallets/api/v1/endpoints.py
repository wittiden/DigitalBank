from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from app.modules.wallets.contracts.responses import FullWalletInfoResponse
from app.modules.wallets.contracts.schemas import CreateWalletSchema
from app.modules.wallets.service.use_cases import CreateWalletService

wallet_router = APIRouter(prefix='/api/wallets')


@wallet_router.post('/create_wallet', response_model=FullWalletInfoResponse, tags=['user', 'create_wallet'], summary='Create credit wallet')
@inject
async def create_credit_wallet_endpoint(schema: CreateWalletSchema, service: FromDishka[CreateWalletService]):
    return await service.create_credit_wallet(schema.pin, schema.email, schema.password)