from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.config import settings
from core.database import engine, Base
from core.models import *
from routers import users, health, preferences, meal_plan, agent, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        from knowledge_base.init_data import init_knowledge_base
        await init_knowledge_base()
    except Exception as e:
        print(f"知识库初始化跳过: {e}")
    yield

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(users.router)
app.include_router(health.router)
app.include_router(preferences.router)
app.include_router(meal_plan.router)
app.include_router(agent.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}