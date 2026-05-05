from uuid import UUID
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.modules.users.contracts.responses import FullUserInfoResponse, SecurityUserInfoResponse
from app.modules.users.contracts.schemas import CreateUserSchema, UpdateUserSchema
from app.modules.users.service.use_cases import CreateUserService, ShowUserService, UpdateUserService, DeleteUserService

user_router = APIRouter(prefix='/api/users')


@user_router.post('/create_user', response_model=FullUserInfoResponse, tags=['user', 'create'], summary='Create user')
@inject
async def create_user_endpoint(schema: CreateUserSchema, service: FromDishka[CreateUserService]):
    user = await service.create_user(schema.name, schema.email, schema.password)
    return user


@user_router.post('/create_admin', response_model=FullUserInfoResponse, tags=['admin', 'create'], summary='Create admin')
@inject
async def create_admin_endpoint(schema: CreateUserSchema, service: FromDishka[CreateUserService]):
    admin = await service.create_admin(schema.name, schema.email, schema.password)
    return admin


@user_router.patch('/update', response_model=SecurityUserInfoResponse, tags=['user', 'update'], summary='Update user')
@inject
async def update_user_endpoint(schema: UpdateUserSchema, service: FromDishka[UpdateUserService]):
    obj = await service.portion_update_user(schema.email, schema.password, schema.data)
    return obj


@user_router.delete('/delete', tags=['admin', 'delete'], summary='Delete user')
@inject
async def delete_user_by_id_endpoint(user_id: UUID, service: FromDishka[DeleteUserService]):
    await service.delete_user_by_id(user_id)
    return {'Success': True}


@user_router.get('/get_user_by_id/{user_id}', response_model=FullUserInfoResponse, tags=['admin', 'get'], summary='Get user by id')
@inject
async def get_user_by_id_endpoint(user_id: UUID, service: FromDishka[ShowUserService]):
    obj = await service.show_user_by_id(user_id)
    return obj


@user_router.get('/get_user', response_model=SecurityUserInfoResponse, tags=['admin', 'get'], summary='Get user by email')
@inject
async def get_user_by_email_endpoint(service: FromDishka[ShowUserService], email: str = 'user@example.com'):
    obj = await service.show_user_by_email(email)
    return obj


@user_router.get('/get_users', response_model=list[FullUserInfoResponse], tags=['admin', 'get'], summary='Get users')
@inject
async def get_users_endpoint(service: FromDishka[ShowUserService], offset: int = 0, limit: int = 100):
    objs = await service.show_users(offset, limit)
    return objs
