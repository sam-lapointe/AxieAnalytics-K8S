import logging
import asyncpg
import asyncio
import json
from aio_pika import Message, connect
from transaction import Transaction
from sales import StoreSales
from web3 import AsyncWeb3
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# Global variables
db_connection = None
w3 = None
dependencies_lock = asyncio.Lock()
dependencies_initialized = False


async def init_dependencies():
    """
    Initialize dependencies for the app.
    This function is called when the app starts.
    """
    global db_connection, w3, dependencies_initialized

    if dependencies_initialized:
        return

    async with dependencies_lock:
        if dependencies_initialized:
            return

        logging.info("Initializing dependencies...")

        if not db_connection:
            # Initialize PostgreSQL connection
            try:
                db_connection_string = await Config.get_pg_connection_string()
                db_connection = await asyncpg.create_pool(
                    dsn=db_connection_string,
                    min_size=1,
                    max_size=10,
                )
                logging.info("PostgreSQL connection initialized.")
            except Exception as e:
                logging.error(f"Error initializing PostgreSQL connection: {e}")
                raise e

        if not w3:
            # Initialize Web3 provider
            try:
                w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(Config.get_node_provider()))
                logging.info("Web3 provider initialized.")
            except Exception as e:
                logging.error(f"Error initializing Web3 provider: {e}")
                raise e

        dependencies_initialized = True


async def process_message(message: Message):
    """
    Process a message from the RabbitMQ queue.
    This function is called when a message is received.
    """
    global db_connection, w3

    try:
        message_body = json.loads(message.body.decode("utf-8"))
        transaction_hash = message_body["transactionHash"]
        block_number = message_body["blockNumber"]
        block_timestamp = message_body["blockTimestamp"]

        # Call Transaction class to get the sales list from a transaction hash.
        sales_list = await Transaction(db_connection, w3).process_logs(transaction_hash)

        # Call the StoreSales class to store the sales in the database and send message to the axies topic.
        if sales_list:
            await StoreSales(
                db_connection,
                rabbitmq_connection=Config.get_rabbitmq_connection_string(),
                rabbitmq_axies_queue_name=Config.get_rabbitmq_queue_axies_name(),
                sales_list=sales_list,
                block_number=block_number,
                block_timestamp=block_timestamp,
                transaction_hash=transaction_hash,
            ).add_to_db()
        else:
            logging.info("Sales list is empty.")

        logging.info(
            f"All sales of transaction {transaction_hash} have been processed successfully."
        )

        # Acknowledge the message after successful processing.
        await message.ack()

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise e


async def store_axie_sales():
    # Ensure dependencies are initialized
    await init_dependencies()

    try:
        connection = await connect(Config.get_rabbitmq_connection_string())
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=5)  # Process 5 messages at a time.

            queue = await channel.declare_queue(
                Config.get_rabbitmq_queue_sales_name(), durable=True
            )

            await queue.consume(process_message)
            await asyncio.Future()  # Keep the connection open for consuming messages.

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise e


if __name__ == "__main__":
    asyncio.run(store_axie_sales())
