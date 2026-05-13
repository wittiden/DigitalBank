from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dishka.integrations.fastapi import FromDishka, inject

from app.modules.auth.service.use_cases import ShowCurrentUserService
from app.database.models import UserModel

health_router = APIRouter(prefix='/api/v1', tags=['health'])

security = HTTPBearer()


def get_token(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return creds.credentials


@inject
async def current_user(service: FromDishka[ShowCurrentUserService], token: str = Depends(get_token)) -> 'UserModel':
    return await service.show_current_user(token)

@inject
async def current_admin(service: FromDishka[ShowCurrentUserService], token: str = Depends(get_token)) -> 'UserModel':
    return await service.show_current_admin(token)


CurrentUser = Annotated[UserModel, Depends(current_user)]
CurrentAdmin = Annotated[UserModel, Depends(current_admin)]


@health_router.get('/health')
async def health_check_endpoint() -> dict[str, str]:
    return {
        'status': 'healthy'
    }
