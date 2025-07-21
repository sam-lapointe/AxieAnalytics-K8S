import asyncpg
import logging
import redis.asyncio as redis
import json
import base64
from azure.identity.aio import DefaultAzureCredential


database = None
redis_client = None


class Postgres:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string


    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.db_connection_string,
                ssl="require",
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
    def __init__(self, host, port=6380):
        self.host = host
        self.port = port
        self.scope = "https://redis.azure.com/.default"
        self.username = None
        self.password = None
        self.client = None
        self.token_expiration = None

    async def connect(self):
        try:
            if not self.password or not self.username:
                await self.refresh_token()

            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                ssl=True,
                username=self.username,
                password=self.password,
                decode_responses=True,
            )
            logging.info("[Redis.connect] Connected to Redis successfully.")
        except Exception as e:
            logging.error(f"[Redis.connect] Error connecting to Redis: {e}")
            raise e

    async def refresh_token(self) -> None:
        try:
            async with DefaultAzureCredential() as credential:
                tmp_token = await credential.get_token(self.scope)
                if tmp_token:
                    self.password = tmp_token.token
                    self._set_token_expiration()
                if not self.username:
                    self._set_username()
                if self.client:
                    await self.client.execute_command("AUTH", self.username, self.password)
            logging.info("[Redis.refresh_token] Token refreshed successfully.")
        except Exception as e:
            logging.error(f"[Redis.refresh_token] Error refreshing Redis token: {e}")
            raise e

    async def disconnect(self):
        if self.client:
            await self.client.aclose()

    def _set_username(self) -> None:
        parts = self.password.split(".")
        base64_str = parts[1]

        if len(base64_str) % 4 == 2:
            base64_str += "=="
        elif len(base64_str) % 4 == 3:
            base64_str += "="

        json_bytes = base64.b64decode(base64_str)
        json_str = json_bytes.decode("utf-8")
        jwt = json.loads(json_str)

        self.username = jwt["oid"]

    def _set_token_expiration(self) -> None:
        parts = self.password.split(".")
        base64_str = parts[1]

        if len(base64_str) % 4 == 2:
            base64_str += "=="
        elif len(base64_str) % 4 == 3:
            base64_str += "="

        json_bytes = base64.b64decode(base64_str)
        json_str = json_bytes.decode("utf-8")
        jwt = json.loads(json_str)

        self.token_expiration = jwt["exp"]