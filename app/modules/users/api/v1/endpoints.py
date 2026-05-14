from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.api.v1.endpoints import CurrentAdmin, CurrentUser
from app.modules.users.contracts.responses import FullUserInfoResponse, SecurityUserInfoResponse
from app.modules.users.contracts.schemas import CreateUserSchema, UpdateUserSchema
from app.modules.users.service.use_cases import CreateUserService, DeleteUserService, ManageUserService, ShowUserService, UpdateUserService
from app.unit_of_work.uow import UnitOfWork

user_router = APIRouter(prefix='/api/v1/users', tags=['users'])
admin_router = APIRouter(prefix='/api/v1/admin/users', tags=['admin'])


@user_router.post('/', response_model=SecurityUserInfoResponse, summary='Create user')
@inject
async def create_user_endpoint(schema: CreateUserSchema, service: FromDishka[CreateUserService], uow: FromDishka[UnitOfWork]) -> SecurityUserInfoResponse:
    dto = await service.create_user(schema.name, schema.email, schema.password)
    return SecurityUserInfoResponse.model_validate(dto)


@admin_router.post('/', response_model=SecurityUserInfoResponse, summary='Create admin')
@inject
async def create_admin_endpoint(schema: CreateUserSchema, service: FromDishka[CreateUserService], uow: FromDishka[UnitOfWork]) -> SecurityUserInfoResponse:
    dto = await service.create_admin(schema.name, schema.email, schema.password)
    return SecurityUserInfoResponse.model_validate(dto)


@user_router.patch('/me', response_model=SecurityUserInfoResponse, summary='Update me')
@inject
async def update_me_endpoint(current_user: CurrentUser, schema: UpdateUserSchema, service: FromDishka[UpdateUserService], uow: FromDishka[UnitOfWork]) -> SecurityUserInfoResponse:
    dto = await service.partial_update_my_user(current_user, schema.model_dump(exclude_none=True))
    return SecurityUserInfoResponse.model_validate(dto)


@admin_router.delete('/{user_id}', summary='Delete user')
@inject
async def delete_user_by_id_endpoint(current_user: CurrentAdmin, user_id: UUID, service: FromDishka[DeleteUserService], uow: FromDishka[UnitOfWork]) -> None:
    await service.delete_user_by_id(current_user, user_id)


@user_router.delete('/me', summary='Close user')
@inject
async def close_user_endpoint(current_user: CurrentUser, service: FromDishka[DeleteUserService], uow: FromDishka[UnitOfWork]) -> None:
    await service.close_my_user(current_user)


@admin_router.patch('/block/{user_id}', summary='Block user')
@inject
async def block_user_endpoint(current_user: CurrentAdmin, user_id: UUID, service: FromDishka[ManageUserService], uow: FromDishka[UnitOfWork]) -> None:
    await service.block_user(current_user, user_id)


@admin_router.patch('/unblock/{user_id}', summary='Unblock user')
@inject
async def unblock_user_endpoint(current_user: CurrentAdmin, user_id: UUID, service: FromDishka[ManageUserService], uow: FromDishka[UnitOfWork]) -> None:
    await service.unblock_user(current_user, user_id)


@admin_router.get('/{user_id}', response_model=FullUserInfoResponse, summary='Get user by id')
@inject
async def get_user_by_id_endpoint(current_user: CurrentAdmin, user_id: UUID, service: FromDishka[ShowUserService], uow: FromDishka[UnitOfWork]) -> FullUserInfoResponse:
    dto = await service.show_user_by_id(current_user, user_id)
    return FullUserInfoResponse.model_validate(dto)


@admin_router.get('/', response_model=list[FullUserInfoResponse], summary='Get users')
@inject
async def get_users_endpoint(
    current_user: CurrentAdmin, service: FromDishka[ShowUserService], uow: FromDishka[UnitOfWork], offset: int = 0, limit: int = 100
) -> list[FullUserInfoResponse]:
    dtos = await service.show_users(current_user, offset, limit)
    return [FullUserInfoResponse.model_validate(dto) for dto in dtos]


@user_router.get('/me', response_model=SecurityUserInfoResponse, summary='Get me')
@inject
async def get_my_user_endpoint(current_user: CurrentUser, service: FromDishka[ShowUserService], uow: FromDishka[UnitOfWork]) -> SecurityUserInfoResponse:
    dto = await service.show_my_user(current_user)
    return SecurityUserInfoResponse.model_validate(dto)
