from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from dishka.integrations.fastapi import setup_dishka
from app.api.v1.endpoints import operation_router
from app.common.exceptions.exceptions import RouterError
from app.common.settings.logger import add_logger
from app.di.container import async_container

from app.common.exceptions.handler import app_exception_handler
from app.modules.balances.api.v1.endpoints import user_balance_router, admin_balance_router
from app.modules.transactions.api.v1.endpoints import admin_trn_router
from app.modules.users.api.v1.endpoints import user_router, admin_router
from app.modules.wallets.api.v1.endpoints import user_wallet_router, admin_wallet_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Application start')

    yield

    logger.info('Application end')


add_logger()

app = FastAPI(lifespan=lifespan)
app.add_exception_handler(RouterError, app_exception_handler)
setup_dishka(async_container, app)

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(user_wallet_router)
app.include_router(admin_wallet_router)
app.include_router(admin_trn_router)
app.include_router(user_balance_router)
app.include_router(admin_balance_router)
app.include_router(operation_router)


