from uuid import UUID
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.modules.users.contracts.responses import FullUserInfoResponse, SecurityUserInfoResponse
from app.modules.users.contracts.schemas import CreateUserSchema, UpdateUserSchema
from app.modules.users.service.use_cases import CreateUserService, ShowUserService, UpdateUserService, \
    DeleteUserService, ManageUserService

user_router = APIRouter(prefix='/api/users', tags=['users'])
admin_router = APIRouter(prefix='/api/users/admin', tags=['admin'])


@user_router.post('/create_user', response_model=SecurityUserInfoResponse, tags=['create'], summary='Create user')
@inject
async def create_user_endpoint(schema: CreateUserSchema, service: FromDishka[CreateUserService]):
    user = await service.create_user(schema.name, schema.email, schema.password)
    return user


@admin_router.post('/create_admin', response_model=SecurityUserInfoResponse, tags=['create'], summary='Create admin')
@inject
async def create_admin_endpoint(schema: CreateUserSchema, service: FromDishka[CreateUserService]):
    admin = await service.create_admin(schema.name, schema.email, schema.password)
    return admin


@user_router.patch('/update_user', response_model=SecurityUserInfoResponse, tags=['update'], summary='Update user')
@inject
async def update_user_endpoint(schema: UpdateUserSchema, service: FromDishka[UpdateUserService]):
    obj = await service.partial_update_user(schema.email, schema.password, schema.data)
    return obj


@admin_router.delete('/delete_user', tags=['delete'], summary='Delete user')
@inject
async def delete_user_by_id_endpoint(user_id: UUID, service: FromDishka[DeleteUserService]):
    await service.delete_user_by_id(user_id)
    return {'Success': True}


@admin_router.patch('/block_user/{user_id}', tags=['manage'], summary='Block user')
@inject
async def block_user_endpoint(user_id: UUID, service: FromDishka[ManageUserService]):
    await service.block_user(user_id)
    return {'Success': True}


@admin_router.patch('/unblock_user/{user_id}', tags=['manage'], summary='Unblock user')
@inject
async def unblock_user_endpoint(user_id: UUID, service: FromDishka[ManageUserService]):
    await service.unblock_user(user_id)
    return {'Success': True}


@admin_router.get('/get_user_by_id/{user_id}', response_model=FullUserInfoResponse, tags=['get'], summary='Get user by id')
@inject
async def get_user_by_id_endpoint(user_id: UUID, service: FromDishka[ShowUserService]):
    obj = await service.show_user_by_id(user_id)
    return obj


@user_router.get('/get_user', response_model=SecurityUserInfoResponse, tags=['get'], summary='Get user by email')
@inject
async def get_user_by_email_endpoint(service: FromDishka[ShowUserService], email: str = 'user@example.com'):
    obj = await service.show_user_by_email(email)
    return obj


@admin_router.get('/get_users', response_model=list[FullUserInfoResponse], tags=['get'], summary='Get users')
@inject
async def get_users_endpoint(service: FromDishka[ShowUserService], offset: int = 0, limit: int = 100):
    objs = await service.show_users(offset, limit)
    return objs
