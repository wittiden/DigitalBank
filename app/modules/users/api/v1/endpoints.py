from uuid import UUID
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.modules.users.contracts.responses import FullUserInfoResponse, SecurityUserInfoResponse
from app.modules.users.contracts.schemas import CreateUserSchema, UpdateUserSchema
from app.modules.users.contracts.schemas import ShowMyUserSchema
from app.modules.users.service.use_cases import CreateUserService, ShowUserService, UpdateUserService, \
    DeleteUserService, ManageUserService

user_router = APIRouter(prefix='/api/users', tags=['users'])
admin_router = APIRouter(prefix='/api/admin/users', tags=['admin'])


@user_router.post('/', response_model=SecurityUserInfoResponse, summary='Create user')
@inject
async def create_user_endpoint(schema: CreateUserSchema, service: FromDishka[CreateUserService]) -> SecurityUserInfoResponse:
    user = await service.create_user(schema.name, schema.email, schema.password)
    return user


@admin_router.post('/', response_model=SecurityUserInfoResponse, summary='Create admin')
@inject
async def create_admin_endpoint(schema: CreateUserSchema, service: FromDishka[CreateUserService]) -> SecurityUserInfoResponse:
    admin = await service.create_admin(schema.name, schema.email, schema.password)
    return admin


@user_router.patch('/me', response_model=SecurityUserInfoResponse, summary='Update user')
@inject
async def update_me_endpoint(schema: UpdateUserSchema, service: FromDishka[UpdateUserService]) -> SecurityUserInfoResponse:
    obj = await service.partial_update_user(schema.email, schema.password, schema.data)
    return obj


@admin_router.delete('/{user_id}', summary='Delete user')
@inject
async def delete_user_by_id_endpoint(user_id: UUID, service: FromDishka[DeleteUserService]) -> None:
    await service.delete_user_by_id(user_id)


@admin_router.patch('/block/{user_id}', summary='Block user')
@inject
async def block_user_endpoint(user_id: UUID, service: FromDishka[ManageUserService]) -> None:
    await service.block_user(user_id)


@admin_router.patch('/unblock/{user_id}', summary='Unblock user')
@inject
async def unblock_user_endpoint(user_id: UUID, service: FromDishka[ManageUserService]) -> None:
    await service.unblock_user(user_id)


@admin_router.get('/{user_id}', response_model=FullUserInfoResponse, summary='Get user by id')
@inject
async def get_user_by_id_endpoint(user_id: UUID, service: FromDishka[ShowUserService]) -> FullUserInfoResponse:
    obj = await service.show_user_by_id(user_id)
    return obj


@user_router.get('/me', response_model=SecurityUserInfoResponse, summary='Get my user')
@inject
async def get_my_user_endpoint(schema: 'ShowMyUserSchema', service: FromDishka[ShowUserService]) -> SecurityUserInfoResponse:
    obj = await service.show_my_user(schema.email, schema.password)
    return obj


@admin_router.get('/', response_model=list[FullUserInfoResponse], summary='Get users')
@inject
async def get_users_endpoint(service: FromDishka[ShowUserService], offset: int = 0, limit: int = 100) -> list[FullUserInfoResponse]:
    objs = await service.show_users(offset, limit)
    return objs
