from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka

from app.common.global_handler import app_error_handler
from app.di.container import async_container
from app.modules.users.api.v1.endpoints import user_router, admin_router
from app.modules.users.exceptions import UserRouterError
from app.modules.wallets.api.v1.endpoints import user_wallet_router, admin_wallet_router

app = FastAPI()
app.add_exception_handler(UserRouterError, app_error_handler)
setup_dishka(async_container, app)

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(user_wallet_router)
app.include_router(admin_wallet_router)
