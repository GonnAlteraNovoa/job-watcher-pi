from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.dashboard import router as dashboard_router
from app.api.routes import router
from app.config import configure_logging, get_settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    init_db(settings.database_path)
    yield


app = FastAPI(
    title="Job Watcher Pi",
    description="Lightweight job monitoring backend for Raspberry Pi and n8n.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)
app.include_router(dashboard_router)
