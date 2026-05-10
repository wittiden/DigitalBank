from fastapi import APIRouter

health_router = APIRouter(prefix='/api/v1', tags=['health'])


@health_router.get('/health')
async def health_check_endpoint() -> dict[str, str]:
    return {
        'status': 'healthy'
    }
