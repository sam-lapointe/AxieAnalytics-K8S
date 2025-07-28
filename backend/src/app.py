from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from src.core import config
from src.database import db
from src.routes import axie_sales
from src.database.refresh_cache import refresh_graph_overview, refresh_graph_collection, refresh_graph_breed_count, refresh_axie_parts


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Postgres connection
    await config.Config.init_secrets()
    db.database = db.Postgres(config.db_connection_string)
    await db.database.connect()

    # Initialize Redis connection
    db.redis_client = db.Redis(config.Config.get_redis_hostname())
    await db.redis_client.connect()

    # Start the scheduler
    scheduler.start()
    
    yield
    await db.database.disconnect()
    await db.redis_client.disconnect()
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(axie_sales.router, prefix="/axies", tags=["Axies"])