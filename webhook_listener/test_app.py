import os
import hmac
import hashlib
import json
import pytest
from fastapi.testclient import TestClient

try:
    from app import app, Config, SIGNING_KEY
except ValueError:
    os.environ["SIGNING_KEY"] = "abcdef_f4536"
    from app import app, Config, SIGNING_KEY

# Initialize the FastAPI test client
client = TestClient(app)


def sign_request_body(body, signing_key):
    signature = hmac.new(
        bytes(signing_key, "utf-8"),
        msg=bytes(json.dumps(body, separators=(",", ":")), "utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return signature


@pytest.fixture
def mock_config(mocker):
    mocker.patch(
        "app.Config.get_signing_key",
        return_value="mock_signing_key",
    )
    mocker.patch(
        "app.Config.get_authorized_ips",
        return_value=["192.168.0.12", "192.168.0.13"],
    )
    mocker.patch(
        "app.Config.get_rabbitmq_connection_string",
        return_value="amqp://user:password@localhost:5672/",
    )
    mocker.patch(
        "app.Config.get_rabbitmq_queue_name",
        return_value="mock_queue",
    )


@pytest.fixture
def mock_rabbitmq(mocker):
    # Mock the aio_pika connect function
    mock_connect = mocker.patch("app.connect")

    # Create mock objects for the RabbitMQ components
    mock_connection = mocker.MagicMock()
    mock_channel = mocker.MagicMock()
    mock_queue = mocker.MagicMock()
    mock_exchange = mocker.MagicMock()

    # Set up the async context manager for connection
    mock_connect.return_value = mock_connection
    mock_connection.__aenter__ = mocker.AsyncMock(return_value=mock_connection)
    mock_connection.__aexit__ = mocker.AsyncMock(return_value=None)

    # Set up channel methods
    mock_connection.channel = mocker.AsyncMock(return_value=mock_channel)
    mock_channel.declare_queue = mocker.AsyncMock(return_value=mock_queue)

    # Set up queue properties
    mock_queue.name = "test_queue"

    # Set up exchange publishing
    mock_channel.default_exchange = mock_exchange
    mock_exchange.publish = mocker.AsyncMock()

    return {
        "connect": mock_connect,
        "connection": mock_connection,
        "channel": mock_channel,
        "queue": mock_queue,
        "exchange": mock_exchange,
    }


@pytest.fixture
def valid_ip():
    return "192.168.0.12"


@pytest.fixture
def valid_request_body():
    return {
        "webhookId": "wh_kpy9f3j05p4b3hh8",
        "id": "whevt_fjlzk3zu8uq1p0q1",
        "createdAt": "2025-04-10T19:20:21.997Z",
        "type": "GRAPHQL",
        "event": {
            "data": {
                "block": {
                    "hash": "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93",
                    "number": 44153279,
                    "timestamp": 1744312821,
                    "logs": [
                        {
                            "topics": [
                                "0x968d1942d9971cb9c45c722957d854c38f327206399d12ae49ca2f9c5dd06fda"
                            ],
                            "account": {
                                "address": "0xfff9ce5f71ca6178d3beecedb61e7eff1602950e"
                            },
                            "transaction": {
                                "hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                            },
                        }
                    ],
                }
            },
            "sequenceNumber": "10000000000632266001",
            "network": "RONIN_MAINNET",
        },
    }


@pytest.fixture(autouse=True)
def mock_dependencies(mock_config, mock_rabbitmq):
    pass  # Used to initialize multiple fixtures from 1 fixture in the tests.


@pytest.fixture
def valid_signature(valid_request_body):
    return sign_request_body(valid_request_body, SIGNING_KEY)


@pytest.fixture
def valid_request_headers(valid_signature, valid_ip):
    return {"x-alchemy-signature": valid_signature, "x-forwarded-for": valid_ip}


@pytest.fixture(autouse=True)
def create_request():
    def _create_request(body, headers):
        return client.post(
            "/webhook",
            headers=headers,
            json=body,
        )

    return _create_request


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "signature, expected_status",
    [
        ("valid_sig", 200),
        ("19d6dd36cb0e7a4a25a9bb841494ee666d60099bf787149c6088cfab6989cd67", 401),
        (None, 400),
    ],
)
async def test_signature(
    create_request,
    valid_request_body,
    valid_ip,
    valid_signature,
    signature,
    expected_status,
    mock_dependencies,
):
    headers = {
        "x-forwarded-for": valid_ip,
    }

    if signature == "valid_sig":
        headers["x-alchemy-signature"] = valid_signature
    elif signature is not None:
        headers["x-alchemy-signature"] = signature

    response = create_request(valid_request_body, headers)

    assert response.status_code == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ip_address, expected_status",
    [
        ("192.168.0.12", 200),
        ("192.168.0.13", 200),
        ("192.168.0.16", 403),
        ("10.15.205.104", 403),
        (None, 403),
    ],
)
async def test_allow_authorized_ips(
    create_request,
    valid_request_body,
    valid_signature,
    ip_address,
    expected_status,
    mock_dependencies,
):
    headers = {"x-alchemy-signature": valid_signature}

    if ip_address is not None:
        headers["x-forwarded-for"] = ip_address

    response = create_request(valid_request_body, headers)

    assert response.status_code == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ip_address, expected_status",
    [
        ("192.168.0.12", 200),
        ("192.168.0.13", 200),
        ("192.168.0.16", 200),
        ("10.15.205.104", 200),
        (None, 200),
    ],
)
async def test_allow_all_ips(
    mocker,
    create_request,
    valid_request_body,
    valid_signature,
    ip_address,
    expected_status,
    mock_dependencies,
):
    mocker.patch("app.Config.get_authorized_ips", return_value=[])

    headers = {"x-alchemy-signature": valid_signature}

    if ip_address is not None:
        headers["x-forwarded-for"] = ip_address

    response = create_request(valid_request_body, headers)

    assert response.status_code == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_body, expected_status",
    [
        (None, 400),
        (
            # Multiple transactions in logs
            {},
            400,
        ),
        (
            # Missing logs
            {
                "webhookId": "wh_kpy9f3j05p4b3hh8",
                "id": "whevt_fjlzk3zu8uq1p0q1",
                "createdAt": "2025-04-10T19:20:21.997Z",
                "type": "GRAPHQL",
                "event": {
                    "data": {
                        "block": {
                            "hash": "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93",
                            "number": 44153279,
                            "timestamp": 1744312821,
                        }
                    },
                    "sequenceNumber": "10000000000632266001",
                    "network": "RONIN_MAINNET",
                },
            },
            500,
        ),
        (
            # Missing transaction hash in logs[0]
            {
                "webhookId": "wh_kpy9f3j05p4b3hh8",
                "id": "whevt_fjlzk3zu8uq1p0q1",
                "createdAt": "2025-04-10T19:20:21.997Z",
                "type": "GRAPHQL",
                "event": {
                    "data": {
                        "block": {
                            "hash": "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93",
                            "number": 44153279,
                            "timestamp": 1744312821,
                            "logs": [
                                {
                                    "topics": [
                                        "0x968d1942d9971cb9c45c722957d854c38f327206399d12ae49ca2f9c5dd06fda"
                                    ],
                                    "account": {
                                        "address": "0xfff9ce5f71ca6178d3beecedb61e7eff1602950e"
                                    },
                                }
                            ],
                        }
                    },
                    "sequenceNumber": "10000000000632266001",
                    "network": "RONIN_MAINNET",
                },
            },
            500,
        ),
        (
            # Missing Block Number
            {
                "webhookId": "wh_kpy9f3j05p4b3hh8",
                "id": "whevt_fjlzk3zu8uq1p0q1",
                "createdAt": "2025-04-10T19:20:21.997Z",
                "type": "GRAPHQL",
                "event": {
                    "data": {
                        "block": {
                            "hash": "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93",
                            "timestamp": 1744312821,
                            "logs": [
                                {
                                    "topics": [
                                        "0x968d1942d9971cb9c45c722957d854c38f327206399d12ae49ca2f9c5dd06fda"
                                    ],
                                    "account": {
                                        "address": "0xfff9ce5f71ca6178d3beecedb61e7eff1602950e"
                                    },
                                    "transaction": {
                                        "hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                                    },
                                }
                            ],
                        }
                    },
                    "sequenceNumber": "10000000000632266001",
                    "network": "RONIN_MAINNET",
                },
            },
            500,
        ),
    ],
)
async def test_request_body(
    create_request,
    valid_ip,
    request_body,
    expected_status,
    mock_dependencies,
):
    headers = {
        "x-alchemy-signature": sign_request_body(request_body, SIGNING_KEY),
        "x-forwarded-for": valid_ip,
    }

    if request_body is None:
        response = create_request(None, headers)
    else:
        response = create_request(request_body, headers)

    print(f"Status Code: {response.status_code}, Expected: {expected_status}")
    print(request_body)
    assert response.status_code == expected_status


# Test Servicebus Message
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_body, expected_messages",
    [
        (
            # One transaction hash
            {
                "webhookId": "wh_kpy9f3j05p4b3hh8",
                "id": "whevt_fjlzk3zu8uq1p0q1",
                "createdAt": "2025-04-10T19:20:21.997Z",
                "type": "GRAPHQL",
                "event": {
                    "data": {
                        "block": {
                            "hash": "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93",
                            "number": 44153279,
                            "timestamp": 1744312821,
                            "logs": [
                                {
                                    "topics": [
                                        "0x968d1942d9971cb9c45c722957d854c38f327206399d12ae49ca2f9c5dd06fda"
                                    ],
                                    "account": {
                                        "address": "0xfff9ce5f71ca6178d3beecedb61e7eff1602950e"
                                    },
                                    "transaction": {
                                        "hash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                                    },
                                }
                            ],
                        }
                    },
                    "sequenceNumber": "10000000000632266001",
                    "network": "RONIN_MAINNET",
                },
            },
            [
                {
                    "blockNumber": 44153279,
                    "transactionHash": "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb",
                    "blockTimestamp": 1744312821,
                },
            ],
        ),
        (
            # Two transactions hash
            {
                "webhookId": "wh_kpy9f3j05p4b3hh8",
                "id": "whevt_ynzq5pz452iftsx4",
                "createdAt": "2025-04-14T14:26:33.897Z",
                "type": "GRAPHQL",
                "event": {
                    "data": {
                        "block": {
                            "hash": "0xe6732b6fd9f74f1196e3011199970edf7d04a9b4901b728910149ea511501029",
                            "number": 44262595,
                            "timestamp": 1744640793,
                            "logs": [
                                {
                                    "topics": [
                                        "0x968d1942d9971cb9c45c722957d854c38f327206399d12ae49ca2f9c5dd06fda"
                                    ],
                                    "account": {
                                        "address": "0xfff9ce5f71ca6178d3beecedb61e7eff1602950e"
                                    },
                                    "transaction": {
                                        "hash": "0xe0e037c4d46a0af225996f837c99a3ddda1cf8cf317780cbbd393b61414818be"
                                    },
                                },
                                {
                                    "topics": [
                                        "0x968d1942d9971cb9c45c722957d854c38f327206399d12ae49ca2f9c5dd06fda"
                                    ],
                                    "account": {
                                        "address": "0xfff9ce5f71ca6178d3beecedb61e7eff1602950e"
                                    },
                                    "transaction": {
                                        "hash": "0x6e74a5ffc57de196ec3bf733f59df20ff786e94d9f490afbf44a443908443200"
                                    },
                                },
                            ],
                        }
                    },
                    "sequenceNumber": "10000000000741595001",
                    "network": "RONIN_MAINNET",
                },
            },
            [
                {
                    "blockNumber": 44262595,
                    "transactionHash": "0xe0e037c4d46a0af225996f837c99a3ddda1cf8cf317780cbbd393b61414818be",
                    "blockTimestamp": 1744640793,
                },
                {
                    "blockNumber": 44262595,
                    "transactionHash": "0x6e74a5ffc57de196ec3bf733f59df20ff786e94d9f490afbf44a443908443200",
                    "blockTimestamp": 1744640793,
                },
            ],
        ),
    ],
)
async def test_rabbitmq_message(
    create_request,
    valid_ip,
    request_body,
    expected_messages,
    mock_rabbitmq,
    mock_dependencies,
):
    headers = {
        "x-alchemy-signature": sign_request_body(request_body, SIGNING_KEY),
        "x-forwarded-for": valid_ip,
    }

    response = create_request(request_body, headers)
    assert response.status_code == 200

    # Assert that RabbitMQ connection was established with the correct parameters
    mock_rabbitmq["connect"].assert_called_once_with(
        Config.get_rabbitmq_connection_string()
    )

    # Assert that get_queue was called with the correct queue name
    mock_rabbitmq["channel"].declare_queue.assert_called_once_with(
        Config.get_rabbitmq_queue_name(), durable=True
    )

    # Assert that publish was called
    assert mock_rabbitmq["exchange"].publish.call_count == len(expected_messages)

    # Retrieve the messages sent
    sent_messages = mock_rabbitmq["exchange"].publish.call_args_list
    print(sent_messages)

    sent_messages_bodies = [
        json.loads(call[0][0].body.decode("utf-8")) for call in sent_messages
    ]

    # Asserting that all messages have been sent as expected, the order doesn't matter because the messages are not sent in order
    assert sorted(sent_messages_bodies, key=lambda x: x["transactionHash"]) == sorted(
        expected_messages, key=lambda x: x["transactionHash"]
    )
