import pytest
import sys
import os
from pathlib import Path
from azure.identity.aio import DefaultAzureCredential

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from function_app import store_axie_sales
    from config import Config
except ValueError:
    os.environ["KEY_VAULT_NAME"] = "mock_kv"
    os.environ["ServiceBusConnection__fullyQualifiedNamespace"] = (
        "https://mock-servicebus.servicebus.windows.net"
    )
    os.environ["SERVICEBUS_TOPIC_AXIES_NAME"] = "mock_axies"
    os.environ["SERVICEBUS_TOPIC_SALES_NAME"] = "mock_sales"
    os.environ["SERVICEBUS_SALES_SUBSCRIPTION_NAME"] = "mock_store_sales"
    os.environ["KV_PG_USERNAME"] = "mock_username"
    os.environ["KV_PG_PASSWORD"] = "mock_password"
    os.environ["PG_HOST"] = "mock.postgres.database.azure.com"
    os.environ["PG_PORT"] = "5432"
    os.environ["PG_DATABASE"] = "axie_market"
    os.environ["NODE_PROVIDER"] = "https://ronin-mainnet.g.alchemy.com/v2/mock_key"
    from function_app import store_axie_sales
    from config import Config


# Mock the DefaultAzureCredential.
@pytest.fixture
def default_azure_credential(mocker):
    mocker.patch(
        "function_app.DefaultAzureCredential",
        autospec=True,
    )


# Mock the Azure Key Vault Secret client.
@pytest.fixture
def key_vault_secret_client(mocker):
    secret_client = mocker.patch(
        "config.SecretClient",
        autospec=True,
    )
    secret_client_instance = secret_client.return_value.__aenter__.return_value = (
        secret_client
    )
    secret_client_instance.get_secret = mocker.AsyncMock()
    secret_client_instance.get_secret.side_effect = [
        mocker.MagicMock(value="mock_username"),
        mocker.MagicMock(value="mock_password"),
    ]
    return secret_client_instance


# Mock the Database connection.
@pytest.fixture
def conn(mocker):
    connection = mocker.patch(
        "function_app.asyncpg.create_pool",
        new_callable=mocker.AsyncMock,
    )
    return connection


# Mock the Web3 provider.
@pytest.fixture
def w3(mocker):
    w3 = mocker.patch(
        "function_app.AsyncWeb3",
        autospec=True,
    )
    w3_instance = w3.return_value
    w3_instance.provider.disconnect = mocker.AsyncMock()
    return w3_instance


# Mock the ServiceBus client.
@pytest.fixture
def servicebus_client(mocker):
    servicebus_client = mocker.patch(
        "function_app.ServiceBusClient",
        autospec=True,
    )
    servicebus_instance = servicebus_client.return_value.__aenter__.return_value = (
        servicebus_client
    )
    return servicebus_instance


@pytest.mark.asyncio
async def test_config_get_pg_connection_string(mocker, key_vault_secret_client):
    pg_host = os.getenv("PG_HOST")
    pg_port = os.getenv("PG_PORT")
    pg_database = os.getenv("PG_DATABASE")

    connection_string = await Config.get_pg_connection_string(DefaultAzureCredential())

    assert (
        connection_string
        == f"postgres://mock_username:mock_password@{pg_host}:{pg_port}/{pg_database}"
    )
    assert key_vault_secret_client.get_secret.call_count == 2


@pytest.mark.asyncio
async def test_function_app(
    mocker,
    conn,
    w3,
    servicebus_client,
    key_vault_secret_client,
    default_azure_credential,
):
    # Mock the ServiceBusMessage.
    servicebus_message = mocker.MagicMock()
    servicebus_message.get_body.return_value = b'{"blockNumber": 44153279, "blockTimestamp": 1712773221, "transactionHash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"}'

    # Mock Transaction.process_logs
    mock_transaction = mocker.patch(
        "function_app.Transaction",
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
        "function_app.StoreSales",
        autospec=True,
    )
    mock_add_to_db_instance = mock_add_to_db.return_value
    mock_add_to_db_instance.add_to_db = mocker.AsyncMock()

    # Call the function
    await store_axie_sales(servicebus_message)

    # Assertions
    conn.assert_called_once()
    servicebus_client.assert_called_once()
    mock_add_to_db_instance.add_to_db.assert_called_once()
    mock_transaction_instance.process_logs.assert_called_once()
