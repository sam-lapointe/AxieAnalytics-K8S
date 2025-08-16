import asyncpg
import logging
import redis.asyncio as redis
import json
import base64
from src.core import config


database = None
redis_client = None


class Postgres:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string


    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.db_connection_string,
                min_size=1,
                max_size=10,
            )
            logging.info("[Postgres.connect] Connected to Postgres successfully.")
        except Exception as e:
            logging.error(f"[Postgres.connect] Error connecting to Postgres: {e}")
            raise e

    async def disconnect(self):
        await self.pool.close()


class Redis:
    def __init__(self, host, port=6379):
        self.host = host
        self.port = port
        self.client = None

    async def connect(self):
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                ssl=False,
                decode_responses=True,
            )
            logging.info("[Redis.connect] Connected to Redis successfully.")
        except Exception as e:
            logging.error(f"[Redis.connect] Error connecting to Redis: {e}")
            raise e

    async def disconnect(self):
        if self.client:
            await self.client.aclose()
