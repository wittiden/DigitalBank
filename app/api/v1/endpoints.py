from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from app.database.models import UserModel
from app.modules.auth.service.use_cases import ShowCurrentUserService

health_router = APIRouter(prefix='/api/v1', tags=['health'])

security = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


@inject
async def current_user(service: FromDishka[ShowCurrentUserService], token: str = Depends(security)) -> 'UserModel':
    return await service.show_current_user(token)


@inject
async def current_admin(service: FromDishka[ShowCurrentUserService], token: str = Depends(security)) -> 'UserModel':
    return await service.show_current_admin(token)


CurrentUser = Annotated[UserModel, Depends(current_user)]
CurrentAdmin = Annotated[UserModel, Depends(current_admin)]


@health_router.get('/health')
async def health_check_endpoint() -> dict[str, str]:
    return {'status': 'healthy'}
