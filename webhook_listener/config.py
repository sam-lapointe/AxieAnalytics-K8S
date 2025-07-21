import logging
import os


class Config:
    @staticmethod
    def get_key_vault_url() -> str:
        key_vault_name = os.getenv("KEY_VAULT_NAME")
        if not key_vault_name:
            logging.critical("KEY_VAULT_NAME is not set.")
            raise ValueError("KEY_VAULT_NAME environment variable is required.")
        return f"https://{key_vault_name}.vault.azure.net"

    @staticmethod
    def get_authorized_ips() -> list[str]:
        authorized_ips = os.getenv("AUTHORIZED_IPS")
        if not authorized_ips:
            logging.critical("AUTHORIZED_IPS is not set.")
            raise ValueError("AUTHORIZED_IPS environment variable is required.")
        try:
            return list(filter(None, authorized_ips.strip("[]").split(",")))
        except Exception:
            logging.critical("AUTHORIZED_IPS is not a valid list.")
            raise ValueError(
                "AUTHORIZED_IPS environment variable must be a valid list."
            )

    @staticmethod
    def get_signing_key_name() -> str:
        signing_key_name = os.getenv("SIGNING_KEY")
        if not signing_key_name:
            logging.critical("SIGNING_KEY is not set.")
            raise ValueError("SIGNING_KEY environment variable is required.")
        return signing_key_name

    @staticmethod
    def get_servicebus_full_namespace() -> str:
        full_namespace = os.getenv("SERVICEBUS_FULLY_QUALIFIED_NAMESPACE")
        if not full_namespace:
            logging.critical("SERVICEBUS_FULLY_QUALIFIED_NAMESPACE is not set.")
            raise ValueError(
                "SERVICEBUS_FULLY_QUALIFIED_NAMESPACE environment variable is required."
            )
        return full_namespace

    @staticmethod
    def get_servicebus_topic_name() -> str:
        topic_name = os.getenv("SERVICEBUS_TOPIC_NAME")
        if not topic_name:
            logging.critical("SERVICEBUS_TOPIC_NAME is not set.")
            raise ValueError("SERVICEBUS_TOPIC_NAME environment variable is required.")
        return topic_name
