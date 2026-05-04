from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.modules.users.contracts.responses import FullUserInfoResponse
from app.modules.users.contracts.schemas import CreateUserSchema
from app.modules.users.service.use_cases import CreateUserService

user_router = APIRouter()

@user_router.post('/create_user', response_model=FullUserInfoResponse)
@inject
async def create_user_endpoint(schema: CreateUserSchema, service: FromDishka[CreateUserService]):
    user = await service.create_user(name=schema.name, email=schema.email, password=schema.password)
    return user