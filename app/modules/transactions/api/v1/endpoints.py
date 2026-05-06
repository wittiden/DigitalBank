from uuid import UUID
from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from app.modules.transactions.contracts.responses import FullTrnInfoResponse
from app.modules.transactions.service.use_cases import ShowTrnService

admin_trn_router = APIRouter(prefix='/api/admin/transactions', tags=['admin', 'transactions'])


@admin_trn_router.get('/{transaction_id}', response_model=FullTrnInfoResponse, summary='Get transaction by id')
@inject
async def get_trn_by_id_endpoint(transaction_id: UUID, service: FromDishka[ShowTrnService]) -> FullTrnInfoResponse:
    return await service.show_trn_by_id(transaction_id)


@admin_trn_router.get('/', response_model=list[FullTrnInfoResponse], summary='Get all transactions')
@inject
async def get_transactions_endpoint(service: FromDishka[ShowTrnService], offset: int = 0, limit: int = 100) -> list[FullTrnInfoResponse]:
    return await service.show_trns(offset, limit)
