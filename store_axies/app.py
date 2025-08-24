import logging
import asyncpg
import asyncio
import json
from aio_pika import connect, Message
from config import Config
from parts import Part
from axies import Axie


# Global variables
db_connection = None
axie_api_key = None
dependencies_lock = asyncio.Lock()
dependencies_initialized = False


async def init_dependencies():
    """
    Initialize dependencies for the app.
    This function is called when the app starts.
    """
    global db_connection, axie_api_key, dependencies_initialized

    if dependencies_initialized:
        return

    async with dependencies_lock:
        if dependencies_initialized:
            return

        logging.info("Initializing dependencies...")

        if not db_connection:
            # Initialize PostgreSQL connection
            db_connection_string = await Config.get_pg_connection_string()
            db_connection = await asyncpg.create_pool(
                dsn=db_connection_string,
                min_size=1,
                max_size=10,
            )
            logging.info("PostgreSQL connection initialized.")

        if not axie_api_key:
            axie_api_key = await Config.get_axie_api_key()
            logging.info("Axie API key initialized.")

        # Verify if the versions table contain the latest version of parts
        await Part.search_and_update_parts_latest_version(db_connection)
        current_parts_version = await Part.get_current_version(db_connection)
        if not current_parts_version:
            logging.error(
                "Current parts version not found in the database. Please run the init_axie_parts function."
            )
            raise Exception(
                "Current parts version not found in the database. Please run the init_axie_parts function."
            )

        dependencies_initialized = True


async def process_message(message: Message):
    """
    Process a message from the RabbitMQ queue.
    This function is called when a new message is received.
    """
    global db_connection, axie_api_key
    try:
        message_body = json.loads(message.body.decode("utf-8"))

        await Axie(
            db_connection,
            axie_api_key,
            message_body["transaction_hash"],
            message_body["axie_id"],
            message_body["sale_date"],
        ).process_axie_data()

        logging.info(
            f"Processed Axie data for transaction {message_body['transaction_hash']} and axie ID {message_body['axie_id']}."
        )
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        raise e


async def store_axies():
    # Ensure dependencies are initialized
    await init_dependencies()

    try:
        connection = await connect(Config.get_rabbitmq_connection_string())
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=5)  # Process 5 messages at a time

            queue = await channel.declare_queue(
                Config.get_rabbitmq_queue_axies_name(), durable=True
            )

            await queue.consume(process_message)
            await asyncio.Future()
    except Exception as e:
        logging.error(f"Error in store_axies: {e}")
        raise e


if __name__ == "__main__":
    asyncio.run(store_axies())
