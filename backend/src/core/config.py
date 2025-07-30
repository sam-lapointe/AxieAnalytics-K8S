import logging
import os
from urllib.parse import quote_plus


db_connection_string = None
axie_api_key = None


class Config:

    @staticmethod
    async def get_pg_connection_string() -> str:
        try:
            # Retrieve environment variables.
            pg_username = os.getenv("PG_USERNAME")
            pg_password = os.getenv("PG_PASSWORD")
            pg_host = os.getenv("PG_HOST")
            pg_port = os.getenv("PG_PORT")
            pg_database = os.getenv("PG_DATABASE")

            # Validate required environment variables.
            if not pg_username:
                logging.critical("PG_USERNAME is not set.")
                raise ValueError("PG_USERNAME environment variable is required.")
            if not pg_password:
                logging.critical("PG_PASSWORD is not set.")
                raise ValueError("PG_PASSWORD environment variable is required.")
            if not pg_host:
                logging.critical("PG_HOST is not set.")
                raise ValueError("PG_HOST environment variable is required.")
            if not pg_port:
                logging.critical("PG_PORT is not set.")
                raise ValueError("PG_PORT environment variable is required.")
            if not pg_database:
                logging.critical("PG_DATABASE is not set.")
                raise ValueError("PG_DATABASE environment variable is required.")

            # Construct the connection string.
            connection_string = f"postgres://{pg_username}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
            return connection_string

        except Exception as e:
            logging.error(f"Error constructing PostgreSQL connection string: {e}")
            raise e

    @staticmethod
    def get_redis_hostname() -> str:
        redis_host = os.getenv("REDIS_HOST")
        if not redis_host:
            logging.critical("REDIS_HOST is not set.")
            raise ValueError("REDIS_HOST environment variable is required.")
        return redis_host

    @staticmethod
    async def init_secrets() -> None:
        global db_connection_string, axie_api_key

        logging.info("[Config.init_secrets] Using local environment variables for secrets.")
        db_connection_string = await Config.get_pg_connection_string()
        logging.info("[Config.init_secrets] Secrets initialized successfully.")
