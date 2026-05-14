from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.auth.contracts.responses import TokenInfoResponse
from app.modules.auth.service.use_cases import AuthService
from app.unit_of_work.uow import UnitOfWork

auth_router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@auth_router.post('/login', response_model=TokenInfoResponse, include_in_schema=False)
@inject
async def login_user_endpoint(service: FromDishka[AuthService], uow: FromDishka[UnitOfWork], request_form: OAuth2PasswordRequestForm = Depends()) -> TokenInfoResponse:
    dto = await service.login_user(request_form.username, request_form.password)
    return TokenInfoResponse.model_validate(dto)
