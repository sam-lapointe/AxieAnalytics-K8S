import azure.functions as func
import logging
import ast
import asyncpg
import asyncio
from datetime import datetime, timezone
from transaction import Transaction
from sales import StoreSales
from azure.identity.aio import DefaultAzureCredential
from azure.servicebus.aio import ServiceBusClient
from web3 import AsyncWeb3
from config import Config


# Global variables
credential = DefaultAzureCredential()
servicebus_client = None
db_connection = None
w3 = None
servicebus_topic_sales_subscription_name = (
    Config.get_servicebus_topic_sales_subscription_name()
)
servicebus_topic_sales_name = Config.get_servicebus_topic_sales_name()
servicebus_topic_axies_name = Config.get_servicebus_topic_axies_name()
dependencies_lock = asyncio.Lock()
dependencies_initialized = False


async def init_dependencies():
    """
    Initialize dependencies for the function app.
    This function is called when the function app starts.
    """
    global servicebus_client, db_connection, w3, dependencies_initialized

    if dependencies_initialized:
        return

    async with dependencies_lock:
        if dependencies_initialized:
            return

        logging.info("Initializing dependencies...")

        if not servicebus_client:
            # Initialize Service Bus client and sender.
            servicebus_namespace = Config.get_servicebus_full_namespace()
            servicebus_client = ServiceBusClient(
                fully_qualified_namespace=servicebus_namespace,
                credential=credential,
                logging_enable=True,
            )
            logging.info(
                f"Service Bus client initialized for namespace: {servicebus_namespace}"
            )

        if not db_connection:
            # Initialize PostgreSQL connection
            db_connection_string = await Config.get_pg_connection_string(credential)
            db_connection = await asyncpg.create_pool(
                dsn=db_connection_string,
                ssl="require",
                min_size=1,
                max_size=10,
            )
            logging.info("PostgreSQL connection initialized.")

        if not w3:
            # Initialize Web3 provider
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(Config.get_node_provider()))
            logging.info("Web3 provider initialized.")

        dependencies_initialized = True


app = func.FunctionApp()


@app.service_bus_topic_trigger(
    arg_name="azservicebus",
    subscription_name=servicebus_topic_sales_subscription_name,
    topic_name=servicebus_topic_sales_name,
    connection="ServiceBusConnection",
)
async def store_axie_sales(azservicebus: func.ServiceBusMessage):
    global servicebus_client, db_connection, w3

    # Ensure dependencies are initialized
    await init_dependencies()

    try:
        message_body = ast.literal_eval(azservicebus.get_body().decode("utf-8"))
        logging.info(
            "Python ServiceBus Topic trigger processed a message: %s", message_body
        )

        transaction_hash = message_body["transactionHash"]
        block_number = message_body["blockNumber"]
        block_timestamp = message_body["blockTimestamp"]

        # Call Transaction class to get the sales list from a transaction hash.
        sales_list = await Transaction(db_connection, w3).process_logs(transaction_hash)

        # Call the StoreSales class to store the sales in the database and send message to the axies topic.
        if sales_list:
            await StoreSales(
                db_connection,
                servicebus_client=servicebus_client,
                servicebus_topic_axies_name=servicebus_topic_axies_name,
                sales_list=sales_list,
                block_number=block_number,
                block_timestamp=block_timestamp,
                transaction_hash=transaction_hash,
            ).add_to_db()
        else:
            logging.info("Sales list is empty.")

        logging.info(
            f"All sales of transaction {transaction_hash} have been processed successfuly."
        )
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise e


@app.timer_trigger(
    arg_name="timer",
    schedule="0 */1 * * * *",  # Every minute
    use_monitoring=False,
)
def timer_function(timer: func.TimerRequest) -> None:
    """
    Time function to keep the function app alive.
    """
    current_time_utc = datetime.now(timezone.utc)
    logging.info("Python timer trigger function ran at %s", current_time_utc)
    # This function is used to keep the function app alive.
    # It does not do anything else.
    # It is called every minute.
