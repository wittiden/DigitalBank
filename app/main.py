from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka

from app.di.container import async_container
from app.modules.users.api.v1.endpoints import user_router

app = FastAPI()
setup_dishka(async_container, app)

app.include_router(user_router)
