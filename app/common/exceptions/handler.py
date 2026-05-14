from fastapi import Request
from fastapi.responses import JSONResponse

from app.common.exceptions.exceptions import RouterError


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, RouterError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                'error': exc.__class__.__name__,
                'detail': exc.detail,
                'path': str(request.url),
            },
        )

    return JSONResponse(
        status_code=500,
        content={
            'error': 'Internal server error'
        }
    )
