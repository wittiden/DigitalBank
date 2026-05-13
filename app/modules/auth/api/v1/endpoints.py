from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.auth.contracts.responses import TokenInfoResponse
from app.modules.auth.contracts.schemas import LoginUserSchema
from app.modules.auth.service.use_cases import AuthService
from app.unit_of_work.uow import UnitOfWork

auth_router = APIRouter(prefix='/api/v1', tags=['auth'])


@auth_router.post('/auth', response_model=TokenInfoResponse, summary='Login user')
@inject
async def login_user_endpoint(schema: LoginUserSchema, service: FromDishka[AuthService], uow: FromDishka[UnitOfWork]) -> TokenInfoDTO:
    token = await service.login_user(schema.email, schema.password)
    return token
