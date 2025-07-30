import logging
import os
from urllib.parse import quote_plus


class Config:
    @staticmethod
    def get_rabbitmq_connection_string() -> str:
        rabbitmq_host = os.getenv("RABBITMQ_HOST")
        rabbitmq_port = os.getenv("RABBITMQ_PORT")
        rabbitmq_user = os.getenv("RABBITMQ_USER")
        rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")

        if not all([rabbitmq_host, rabbitmq_port, rabbitmq_user, rabbitmq_password]):
            logging.critical("RabbitMQ connection details are not set.")
            raise ValueError("RabbitMQ connection details are required.")

        return f"amqp://{quote_plus(rabbitmq_user)}:{quote_plus(rabbitmq_password)}@{rabbitmq_host}:{rabbitmq_port}/"

    @staticmethod
    def get_rabbitmq_queue_axies_name() -> str:
        queue_name = os.getenv("RABBITMQ_QUEUE_AXIES_NAME")
        if not queue_name:
            logging.critical("RABBITMQ_QUEUE_AXIES_NAME is not set.")
            raise ValueError(
                "RABBITMQ_QUEUE_AXIES_NAME environment variable is required."
            )
        return queue_name

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

            connection_string = f"postgres://{quote_plus(pg_username)}:{quote_plus(pg_password)}@{pg_host}:{pg_port}/{pg_database}"
            return connection_string

        except Exception as e:
            logging.error(f"Error constructing PostgreSQL connection string: {e}")
            raise e

    @staticmethod
    async def get_axie_api_key() -> str:
        try:
            # Retrieve environment variable
            axie_api_key = os.getenv("AXIE_API_KEY_NAME")

            # Validate required environment variable
            if not axie_api_key:
                logging.critical("AXIE_API_KEY is not set.")
                raise ValueError("AXIE_API_KEY environment variable is required.")

            return axie_api_key
        except Exception as e:
            logging.error("Error retrieving the Axie API key.")
            raise e
