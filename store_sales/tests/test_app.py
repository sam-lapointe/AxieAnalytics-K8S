import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["RABBITMQ_HOST"] = "localhost"
os.environ["RABBITMQ_PORT"] = "5672"
os.environ["RABBITMQ_USER"] = "mock_username"
os.environ["RABBITMQ_PASSWORD"] = "mock_password"
os.environ["RABBITMQ_QUEUE_SALES_NAME"] = "mock_sales"
os.environ["RABBITMQ_QUEUE_AXIES_NAME"] = "mock_axies"
os.environ["PG_USERNAME"] = "mock_username"
os.environ["PG_PASSWORD"] = "mock_password"
os.environ["PG_HOST"] = "mock.postgres.database.azure.com"
os.environ["PG_PORT"] = "5432"
os.environ["PG_DATABASE"] = "axie_market"
os.environ["NODE_PROVIDER"] = "https://ronin-mainnet.g.alchemy.com/v2/mock_key"


from app import process_message, init_dependencies
from config import Config


# Mock the Database connection.
@pytest.fixture
def conn(mocker):
    connection = mocker.patch(
        "app.asyncpg.create_pool",
        new_callable=mocker.AsyncMock,
    )
    return connection


# Mock the Web3 provider.
@pytest.fixture
def w3(mocker):
    w3 = mocker.patch(
        "app.AsyncWeb3",
        autospec=True,
    )
    w3_instance = w3.return_value
    w3_instance.provider.disconnect = mocker.AsyncMock()
    return w3_instance


# Mock RabbitMQ
@pytest.fixture
def rabbitmq(mocker):
    # Mock aio_pika.connect
    mock_connection = mocker.AsyncMock()
    mock_channel = mocker.AsyncMock()
    mock_queue = mocker.AsyncMock()

    # Setup the connection/channel/queue chain
    mock_connection.channel.return_value = mock_channel
    mock_channel.declare_queue.return_value = mock_queue
    mock_queue.consume = mocker.AsyncMock()

    # Patch aio_pika.connect to return our mock connection
    mocker.patch("app.connect", return_value=mock_connection)

    return {
        "connection": mock_connection,
        "channel": mock_channel,
        "queue": mock_queue,
    }


@pytest.mark.asyncio
async def test_config_get_pg_connection_string(mocker):
    pg_host = os.getenv("PG_HOST")
    pg_port = os.getenv("PG_PORT")
    pg_database = os.getenv("PG_DATABASE")
    pg_username = os.getenv("PG_USERNAME")
    pg_password = os.getenv("PG_PASSWORD")
    connection_string = await Config.get_pg_connection_string()

    assert (
        connection_string
        == f"postgres://{pg_username}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
    )


@pytest.mark.asyncio
async def test_function_app(
    mocker,
    conn,
    w3,
    rabbitmq,
):
    # Mock the RabbitMQ message.
    rabbitmq_message = mocker.MagicMock()
    rabbitmq_message.body = b'{"blockNumber": 44153279, "blockTimestamp": 1712773221, "transactionHash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"}'

    # Mock the ack method
    rabbitmq_message.ack = mocker.AsyncMock()

    # Mock Transaction.process_logs
    mock_transaction = mocker.patch(
        "app.Transaction",
        autospec=True,
    )
    mock_transaction_instance = mock_transaction.return_value
    mock_transaction_instance.process_logs.return_value = [
        {
            "price_weth": 0.001836535870831618,
            "axie_id": 11649154,
        }
    ]

    # Mock StoreSales.add_to_db
    mock_add_to_db = mocker.patch(
        "app.StoreSales",
        autospec=True,
    )
    mock_add_to_db_instance = mock_add_to_db.return_value
    mock_add_to_db_instance.add_to_db = mocker.AsyncMock()

    # Call the functions. Both of these are called in the store_axie_sales function.
    await init_dependencies()
    await process_message(rabbitmq_message)

    # Assertions
    conn.assert_called_once()
    mock_add_to_db_instance.add_to_db.assert_called_once()
    mock_transaction_instance.process_logs.assert_called_once()
