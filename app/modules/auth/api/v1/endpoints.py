from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.api.v1.endpoints import CurrentUser
from app.modules.auth.contracts.responses import TokenInfoResponse
from app.modules.auth.contracts.schema import LoginUserSchema, RefreshTokensSchema
from app.modules.auth.service.use_cases import AuthService
from app.unit_of_work.uow import UnitOfWork

auth_router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@auth_router.post('/login', response_model=TokenInfoResponse, summary='Login user')
@inject
async def login_user_endpoint(schema: LoginUserSchema, service: FromDishka[AuthService], uow: FromDishka[UnitOfWork]) -> TokenInfoResponse:
    dto = await service.login_user(schema.email, schema.password)
    return TokenInfoResponse.model_validate(dto)


@auth_router.post('/logout', summary='Logout user')
@inject
async def logout_user_endpoint(current_user: CurrentUser, service: FromDishka[AuthService], uow: FromDishka[UnitOfWork]) -> None:
    await service.logout_user(current_user)


@auth_router.post('/refresh', response_model=TokenInfoResponse, summary='Refresh tokens')
@inject
async def refresh_tokens_endpoint(schema: RefreshTokensSchema, service: FromDishka[AuthService], uow: FromDishka[UnitOfWork]) -> TokenInfoResponse:
    dto = await service.refresh_tokens(schema.refresh_token)
    return TokenInfoResponse.model_validate(dto)
