from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.admin import setup_admin
from app.database import Base, engine
from app.routers import api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="TakeDone", version="0.1.0", lifespan=lifespan)
app.include_router(api_router)

# Подключение админ-панели
setup_admin(app, engine)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}