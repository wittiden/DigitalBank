from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse

from app.modules.users.exceptions import AppError


async def app_error_handler(request: Request, exc: AppError):
    logger.warning(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': exc.__class__.__name__,
            'detail': exc.detail,
        }
    )

