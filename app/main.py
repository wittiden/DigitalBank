from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka

from app.di.container import async_container


app = FastAPI()
setup_dishka(async_container, app)
