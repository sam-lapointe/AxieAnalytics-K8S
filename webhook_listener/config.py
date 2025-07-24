import logging
import os


class Config:
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
    def get_signing_key() -> str:
        signing_key = os.getenv("SIGNING_KEY")
        if not signing_key:
            logging.critical("SIGNING_KEY is not set.")
            raise ValueError("SIGNING_KEY environment variable is required.")
        return signing_key

    @staticmethod
    def get_rabbitmq_connection_string() -> str:
        rabbitmq_host = os.getenv("RABBITMQ_HOST")
        rabbitmq_port = os.getenv("RABBITMQ_PORT")
        rabbitmq_user = os.getenv("RABBITMQ_USER")
        rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")

        if not all([rabbitmq_host, rabbitmq_port, rabbitmq_user, rabbitmq_password]):
            logging.critical("RabbitMQ connection details are not set.")
            raise ValueError("RabbitMQ connection details are required.")

        return f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}:{rabbitmq_port}/"

    @staticmethod
    def get_rabbitmq_queue_name() -> str:
        queue_name = os.getenv("RABBITMQ_QUEUE_NAME")
        if not queue_name:
            logging.critical("RABBITMQ_QUEUE_NAME is not set.")
            raise ValueError("RABBITMQ_QUEUE_NAME environment variable is required.")
        return queue_name
