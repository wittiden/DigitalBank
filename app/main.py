from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka

from app.common.global_handler import app_error_handler
from app.di.container import async_container
from app.modules.users.api.v1.endpoints import user_router
from app.modules.users.exceptions import AppError

app = FastAPI()
app.add_exception_handler(AppError, app_error_handler)
setup_dishka(async_container, app)

app.include_router(user_router)
