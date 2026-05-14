from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.api.v1.endpoints import CurrentAdmin
from app.modules.transactions.contracts.responses import FullTrnInfoResponse
from app.modules.transactions.service.use_cases import ShowTrnService
from app.unit_of_work.uow import UnitOfWork

admin_trn_router = APIRouter(prefix='/api/v1/admin/transactions', tags=['transactions'])


@admin_trn_router.get('/{transaction_id}', response_model=FullTrnInfoResponse, summary='Get transaction by id')
@inject
async def get_trn_by_id_endpoint(current_user: CurrentAdmin, transaction_id: UUID, service: FromDishka[ShowTrnService], uow: FromDishka[UnitOfWork]) -> FullTrnInfoResponse:
    dto = await service.show_trn_by_id(current_user, transaction_id)
    return FullTrnInfoResponse.model_validate(dto)


@admin_trn_router.get('/', response_model=list[FullTrnInfoResponse], summary='Get all transactions')
@inject
async def get_transactions_endpoint(
    current_user: CurrentAdmin, service: FromDishka[ShowTrnService], uow: FromDishka[UnitOfWork], offset: int = 0, limit: int = 100
) -> list[FullTrnInfoResponse]:
    dtos = await service.show_trns(current_user, offset, limit)
    return [FullTrnInfoResponse.model_validate(dto) for dto in dtos]
