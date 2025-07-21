import pytest
import sys
import asyncpg
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sales import (
    datetime,
    timezone,
    StoreSales,
)


# Mock the current time.
@pytest.fixture
def current_time(mocker):
    mock_current_time = datetime(2025, 5, 9, 12, 0, 0, tzinfo=timezone.utc)
    mock_datetime = mocker.patch("sales.datetime")
    mock_datetime.now.return_value = mock_current_time
    return mock_current_time


# Mock the database connection.
@pytest.fixture
def conn(mocker):
    # This will be returned by __aenter__ (used inside the context manager)
    db_conn = mocker.AsyncMock()

    # This is the async context manager returned by conn.acquire()
    acquire_cm = mocker.MagicMock()
    acquire_cm.__aenter__ = mocker.AsyncMock(return_value=db_conn)
    acquire_cm.__aexit__ = mocker.AsyncMock(return_value=None)

    # Mock connection with acquire() returning the context manager
    conn_instance = mocker.AsyncMock()
    conn_instance.acquire = mocker.MagicMock(return_value=acquire_cm)
    return conn_instance


# Mock the ServiceBus client.
@pytest.fixture
def servicebus_client(mocker):
    servicebus_client = mocker.patch(
        "sales.ServiceBusClient",
        autospec=True,
    )
    servicebus_instance = servicebus_client.return_value.__aenter__.return_value = (
        servicebus_client
    )
    return servicebus_instance


# Test the StoreSales.add_to_db method.
@pytest.mark.parametrize(
    "sale_params, already_exists",
    [
        (
            {
                "block_number": 44153279,
                "block_timestamp": 1712773221,
                "transaction_hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
                "sales_list": [
                    {
                        "price_weth": 0.001836535870831618,
                        "axie_id": 11649154,
                    },
                ],
            },
            False,
        ),
        (
            {
                "block_number": 44153279,
                "block_timestamp": 1712773221,
                "transaction_hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
                "sales_list": [
                    {
                        "price_weth": 0.001836535870831618,
                        "axie_id": 11649154,
                    },
                    {
                        "price_weth": 0.02,
                        "axie_id": 123456789,
                    },
                ],
            },
            False,
        ),
        (
            {
                "block_number": 44153279,
                "block_timestamp": 1712773221,
                "transaction_hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
                "sales_list": [
                    {
                        "price_weth": 0.001836535870831618,
                        "axie_id": 11649154,
                    },
                ],
            },
            True,
        ),
        (
            {
                "block_number": 44153279,
                "block_timestamp": 1712773221,
                "transaction_hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
                "sales_list": [],
            },
            False,
        ),
    ],
)
@pytest.mark.asyncio
async def test_add_to_db(
    mocker, current_time, conn, servicebus_client, sale_params, already_exists
):
    # Create the StoreSales instance.
    store_sales = StoreSales(
        conn=conn,
        servicebus_client=servicebus_client,
        servicebus_topic_axies_name="test_topic",
        sales_list=sale_params["sales_list"],
        block_number=sale_params["block_number"],
        block_timestamp=sale_params["block_timestamp"],
        transaction_hash=sale_params["transaction_hash"],
    )

    num_sales = len(sale_params["sales_list"])

    db_connection = await conn.acquire().__aenter__()

    if num_sales == 0:
        # If there are no sales, the function should return early.
        await store_sales.add_to_db()
        db_connection.execute.assert_not_called()
    else:
        # If there are sales, the function should attempt to add them to the database.
        if already_exists:
            # If the sale already exists, it should handle the UniqueViolationError.
            db_connection.execute.side_effect = asyncpg.exceptions.UniqueViolationError(
                "Unique violation"
            )
            await store_sales.add_to_db()
            db_connection.execute.assert_called_once()
            assert db_connection.execute.call_count == num_sales
        else:
            # If the sale does not exist, it should add it to the database.
            db_connection.execute.side_effect = None
            await store_sales.add_to_db()
            assert db_connection.execute.call_count == num_sales

            for i in range(num_sales):
                axie_sale = {
                    "block_number": sale_params["block_number"],
                    "transaction_hash": sale_params["transaction_hash"],
                    "sale_date": sale_params["block_timestamp"],
                    "price_eth": sale_params["sales_list"][i]["price_weth"],
                    "axie_id": sale_params["sales_list"][i]["axie_id"],
                    "created_at": current_time,
                    "modified_at": current_time,
                }

                # The indentation of the query string is important to match the expected format.
                db_connection.execute.assert_any_call(
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


@pytest.mark.parametrize(
    "axie_sale, expected_message",
    [
        (
            {
                "block_number": 44153279,
                "transaction_hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
                "sale_date": 1712773221,
                "price_eth": 0.001836535870831618,
                "axie_id": 11649154,
                "created_at": datetime(2025, 5, 9, 12, 0, 0, tzinfo=timezone.utc),
                "modified_at": datetime(2025, 5, 9, 12, 0, 0, tzinfo=timezone.utc),
            },
            {
                "transaction_hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
                "sale_date": 1712773221,
                "axie_id": 11649154,
            },
        ),
        (
            {
                "block_number": 44153279,
                "transaction_hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
                "sale_date": 1712773221,
                "price_eth": 0.02,
                "axie_id": 123456789,
                "created_at": datetime(2025, 5, 9, 12, 0, 0, tzinfo=timezone.utc),
                "modified_at": datetime(2025, 5, 9, 12, 0, 0, tzinfo=timezone.utc),
            },
            {
                "transaction_hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
                "sale_date": 1712773221,
                "axie_id": 123456789,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_send_topic_message(
    mocker, servicebus_client, axie_sale, expected_message
):
    # Mock the send_messages_with_sender method.
    mocker.patch(
        "sales.StoreSales._StoreSales__send_message_with_sender", return_value=None
    )

    # Create the StoreSales instance.
    store_sales = StoreSales(
        conn=None,
        servicebus_client=servicebus_client,
        servicebus_topic_axies_name="test_topic",
        sales_list=[axie_sale],
        block_number=axie_sale["block_number"],
        block_timestamp=axie_sale["sale_date"],
        transaction_hash=axie_sale["transaction_hash"],
    )

    # Call the method to test.
    await store_sales._StoreSales__send_topic_message(axie_sale)

    # Check that the send_messages_with_sender method was called with the expected message.
    store_sales._StoreSales__send_message_with_sender.assert_called_once_with(
        expected_message
    )


@pytest.mark.parametrize(
    "expected_message",
    [
        {
            "transaction_hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
            "sale_date": 1712773221,
            "axie_id": 11649154,
        },
        {
            "transaction_hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
            "sale_date": 1712773221,
            "axie_id": 123456789,
        },
    ],
)
@pytest.mark.asyncio
async def test_send_message_with_sender(mocker, servicebus_client, expected_message):
    # Mock the servicebus sender.
    servicebus_sender = mocker.AsyncMock()
    servicebus_client.get_topic_sender.return_value.__aenter__.return_value = (
        servicebus_sender
    )
    servicebus_sender.return_value.__aenter__.return_value = servicebus_sender
    servicebus_sender.return_value.__aexit__.return_value = None
    servicebus_sender.send_messages = mocker.AsyncMock()

    store_sales = StoreSales(
        conn=None,
        servicebus_client=servicebus_client,
        servicebus_topic_axies_name="test_topic",
        sales_list=[],
        block_number=44153279,
        block_timestamp=1712773221,
        transaction_hash="0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
    )

    await store_sales._StoreSales__send_message_with_sender(expected_message)

    servicebus_sender.send_messages.assert_called_once()
    sent_message = servicebus_sender.send_messages.call_args[0][0]
    sent_message_body = json.loads(
        b"".join(sent_message.body).decode("utf-8").replace("'", '"')
    )
    assert sent_message_body == expected_message
