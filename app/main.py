from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from dishka.integrations.fastapi import setup_dishka

from app.api.v1.routers import routers
from app.common.exceptions.exceptions import RouterError
from app.common.settings.logger import add_logger
from app.di.container import async_container
from app.common.exceptions.handler import app_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Application start')

    yield

    logger.info('Application end')


add_logger()

app = FastAPI(lifespan=lifespan)
app.add_exception_handler(RouterError, app_exception_handler)
setup_dishka(async_container, app)

for router in routers:
    app.include_router(router)


