import asyncpg
import logging
import asyncio
from asyncpg.exceptions import UniqueViolationError
from datetime import datetime, timezone
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus.exceptions import ServiceBusError


class StoreSales:
    """
    Add sales to DB and call send_message to alert axies service.
    """

    def __init__(
        self,
        conn: asyncpg.Connection,
        servicebus_client: ServiceBusClient,
        servicebus_topic_axies_name: str,
        sales_list: list,
        block_number: int,
        block_timestamp: int,
        transaction_hash: str,
    ):
        self.__conn = conn
        self.__servicebus_client = servicebus_client
        self.__servicebus_topic_axies_name = servicebus_topic_axies_name
        self.__sales_list = sales_list
        self.__block_number = block_number
        self.__block_timestamp = block_timestamp
        self.__transaction_hash = transaction_hash

    async def add_to_db(self) -> None:
        """
        Go through the list of sales and add each of them to the database.
        """
        if not self.__sales_list:
            logging.info("[add_to_db] Sales list is empty. No data to add to DB.")
            return

        async with self.__conn.acquire() as conn:
            for sale in self.__sales_list:
                try:
                    current_time_utc = datetime.now(timezone.utc)

                    axie_sale = {
                        "block_number": self.__block_number,
                        "transaction_hash": self.__transaction_hash,
                        "sale_date": self.__block_timestamp,
                        "price_eth": sale["price_weth"],
                        "axie_id": sale["axie_id"],
                        "created_at": current_time_utc,
                        "modified_at": current_time_utc,
                    }

                    try:
                        await conn.execute(
                            """
                            INSERT INTO axie_sales(
                                block_number,
                                transaction_hash,
                                sale_date,
                                price_eth,
                                axie_id,
                                created_at,
                                modified_at
                            )
                            VALUES (
                                $1, $2, $3, $4, $5, $6, $7
                            )
                            """,
                            *axie_sale.values(),
                        )
                        logging.info(f"[add_to_db] Added to DB Axie sale: {axie_sale}")
                    except UniqueViolationError:
                        logging.info(
                            f"[add_to_db] This axie sale already exists in the database: {axie_sale}"
                        )

                    await self.__send_topic_message(axie_sale)

                except Exception as e:
                    logging.error(
                        f"[add_to_db] An unexpected error occured while adding to DB Axie sale {axie_sale}: {e}"
                    )
                    raise e

        logging.info(
            f"[add_to_db] All sales were added to the database successfuly for transaction {self.__transaction_hash}."
        )

    async def __send_topic_message(self, axie_sale) -> None:
        """
        For each sale, sends a message to axies topic.
        """
        max_retries = 3
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                message = {
                    "transaction_hash": self.__transaction_hash,
                    "sale_date": axie_sale["sale_date"],
                    "axie_id": axie_sale["axie_id"],
                }

                # Send message to the Axies topic.
                logging.info(
                    f"[__send_topic_message] Sending message to axies topic for {axie_sale}."
                )

                """
                This allows to send messages while handling the sender that sometimes hangs for a long period of time.
                """
                await asyncio.wait_for(
                    self.__send_message_with_sender(message),
                    timeout=30,  # seconds
                )
                logging.info(f"[__send_topic_message] Sent message: {message}")
                return
            except asyncio.TimeoutError:
                logging.warning(
                    f"[__send_topic_message] TimeoutError occured while sending message to axies topic for {axie_sale}. Attempt {attempt + 1}/{max_retries}."
                )
            except ServiceBusError as e:
                logging.error(
                    f"[__send_topic_message] ServiceBusError occured while sending message to axies topic for {axie_sale}: {e}. Attempt {attempt + 1}/{max_retries}."
                )
            except Exception as e:
                logging.error(
                    f"[__send_topic_message] An unexpected error occurred while sending message to axies topic for {axie_sale}: {e}. Attempt {attempt + 1} of {max_retries}."
                )
                raise e

            # Wait before retrying
            await asyncio.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff

            if attempt == max_retries - 1:
                logging.error(
                    f"[__send_topic_message] Max retries reached. Failed to send message to axies topic for {axie_sale}."
                )
                raise Exception(
                    f"Failed to send message to axies topic after {max_retries} attempts."
                )

    async def __send_message_with_sender(self, message: dict) -> None:
        """
        Send a message to the axies topic.
        """
        async with self.__servicebus_client.get_topic_sender(
            self.__servicebus_topic_axies_name
        ) as sender:
            await sender.send_messages(ServiceBusMessage(str(message)))
