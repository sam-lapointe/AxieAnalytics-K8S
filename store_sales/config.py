import logging
import os
from urllib.parse import quote_plus
from azure.keyvault.secrets.aio import SecretClient
from azure.identity.aio import DefaultAzureCredential


class Config:
    @staticmethod
    def get_key_vault_url() -> str:
        key_vault_name = os.getenv("KEY_VAULT_NAME")
        if not key_vault_name:
            logging.critical("KEY_VAULT_NAME is not set.")
            raise ValueError("KEY_VAULT_NAME environment variable is required.")
        return f"https://{key_vault_name}.vault.azure.net"

    @staticmethod
    def get_servicebus_full_namespace() -> str:
        full_namespace = os.getenv("ServiceBusConnection__fullyQualifiedNamespace")
        if not full_namespace:
            logging.critical(
                "ServiceBusConnection__fullyQualifiedNamespace is not set."
            )
            raise ValueError(
                "ServiceBusConnection__fullyQualifiedNamespace environment variable is required."
            )
        return full_namespace

    @staticmethod
    def get_servicebus_topic_sales_name() -> str:
        topic_sales_name = os.getenv("SERVICEBUS_TOPIC_SALES_NAME")
        if not topic_sales_name:
            logging.critical("SERVICEBUS_TOPIC_SALES_NAME is not set.")
            raise ValueError(
                "SERVICEBUS_TOPIC_SALES_NAME environment variable is required."
            )
        return topic_sales_name

    @staticmethod
    def get_servicebus_topic_axies_name() -> str:
        topic_axies_name = os.getenv("SERVICEBUS_TOPIC_AXIES_NAME")
        if not topic_axies_name:
            logging.critical("SERVICEBUS_TOPIC_AXIES_NAME is not set.")
            raise ValueError(
                "SERVICEBUS_TOPIC_AXIES_NAME environment variable is required."
            )
        return topic_axies_name

    @staticmethod
    def get_servicebus_topic_sales_subscription_name() -> str:
        subscription_name = os.getenv("SERVICEBUS_SALES_SUBSCRIPTION_NAME")
        if not subscription_name:
            logging.critical("SERVICEBUS_SALES_SUBSCRIPTION_NAME is not set.")
            raise ValueError(
                "SERVICEBUS_SALES_SUBSCRIPTION_NAME environment variable is required."
            )
        return subscription_name

    @staticmethod
    async def get_pg_connection_string(credential: DefaultAzureCredential) -> str:
        try:
            # Retrieve environment variables.
            kv_pg_username = os.getenv("KV_PG_USERNAME")
            kv_pg_password = os.getenv("KV_PG_PASSWORD")
            pg_host = os.getenv("PG_HOST")
            pg_port = os.getenv("PG_PORT")
            pg_database = os.getenv("PG_DATABASE")

            # Validate required environment variables.
            if not kv_pg_username:
                logging.critical("KV_PG_USERNAME is not set.")
                raise ValueError("KV_PG_USERNAME environment variable is required.")
            if not kv_pg_password:
                logging.critical("KV_PG_PASSWORD is not set.")
                raise ValueError("KV_PG_PASSWORD environment variable is required.")
            if not pg_host:
                logging.critical("PG_HOST is not set.")
                raise ValueError("PG_HOST environment variable is required.")
            if not pg_port:
                logging.critical("PG_PORT is not set.")
                raise ValueError("PG_PORT environment variable is required.")
            if not pg_database:
                logging.critical("PG_DATABASE is not set.")
                raise ValueError("PG_DATABASE environment variable is required.")

            async with SecretClient(
                Config.get_key_vault_url(), credential
            ) as key_vault_client:
                # Retrieves the PostgreSQL Credentials from Key Vault and URL encodes them.
                pg_username_secret = await key_vault_client.get_secret(kv_pg_username)
                pg_password_secret = await key_vault_client.get_secret(kv_pg_password)
                pg_username = quote_plus(pg_username_secret.value)
                pg_password = quote_plus(pg_password_secret.value)

            connection_string = f"postgres://{pg_username}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
            return connection_string

        except Exception as e:
            logging.error(f"Error constructing PostgreSQL connection string: {e}")
            raise e

    # Validate required environment variables
    @staticmethod
    def get_node_provider() -> str:
        node_provider_url = os.getenv("NODE_PROVIDER")
        if not node_provider_url:
            logging.critical("NODE_PROVIDER is not set.")
            raise ValueError("NODE_PROVIDER environment variable is required.")
        return node_provider_url
