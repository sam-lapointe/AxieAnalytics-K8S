import os
import hmac
import hashlib
import json
import pytest
from unittest.mock import ANY
from azure.functions import HttpRequest
from azure.identity.aio import DefaultAzureCredential

try:
    from function_app import AlchemyWebhook, Config
except ValueError:
    os.environ["KEY_VAULT_NAME"] = "mock_kv"
    from function_app import AlchemyWebhook, Config


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
        "function_app.Config.get_key_vault_url",
        return_value="https://mock.vault.azure.net",
    )
    mocker.patch(
        "function_app.Config.get_signing_key_name",
        return_value="mock_signing_key",
    )
    mocker.patch(
        "function_app.Config.get_authorized_ips",
        return_value=["192.168.0.12", "192.168.0.13"],
    )
    mocker.patch(
        "function_app.Config.get_servicebus_full_namespace",
        return_value="https://mock-namespace.servicebus.windows.net",
    )
    mocker.patch(
        "function_app.Config.get_servicebus_topic_name",
        return_value="mock_topic",
    )


@pytest.fixture
def mock_key_vault_client(mocker):
    mocker.patch("function_app.SecretClient")


@pytest.fixture
def mock_servicebus(mocker):
    mock_servicebus_client = mocker.patch("function_app.ServiceBusClient")
    mock_servicebus_instance = mocker.MagicMock()
    mock_servicebus_client.return_value.__aenter__.return_value = (
        mock_servicebus_instance
    )

    mock_sender = mocker.MagicMock()
    mock_sender.send_messages = mocker.AsyncMock()
    mock_servicebus_instance.get_topic_sender.return_value.__aenter__.return_value = (
        mock_sender
    )

    return {
        "client": mock_servicebus_client,
        "instance": mock_servicebus_instance,
        "sender": mock_sender,
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


@pytest.fixture
def signing_key():
    return "abcdef_f4536"


@pytest.fixture
def mock_get_signing_key(mocker, signing_key):
    mocker.patch("function_app.get_signing_key", return_value=signing_key)


@pytest.fixture(autouse=True)
def mock_dependencies(
    mock_config, mock_key_vault_client, mock_get_signing_key, mock_servicebus
):
    pass  # Used to initialize multiple fixtures from 1 fixture in the tests.


@pytest.fixture
def valid_signature(valid_request_body, signing_key):
    return sign_request_body(valid_request_body, signing_key)


@pytest.fixture
def valid_request_headers(valid_signature, valid_ip):
    return {"x-alchemy-signature": valid_signature, "x-forwarded-for": valid_ip}


@pytest.fixture(autouse=True)
def create_request():
    def _create_request(body, headers):
        return HttpRequest(
            method="POST",
            url="/webhook",
            headers=headers,
            body=bytes(json.dumps(body, separators=(",", ":")), "utf-8"),
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

    req = create_request(valid_request_body, headers)

    response = await AlchemyWebhook(req)
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

    req = create_request(valid_request_body, headers)

    response = await AlchemyWebhook(req)
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
    mocker.patch("function_app.Config.get_authorized_ips", return_value=[])

    headers = {"x-alchemy-signature": valid_signature}

    if ip_address is not None:
        headers["x-forwarded-for"] = ip_address

    req = create_request(valid_request_body, headers)

    response = await AlchemyWebhook(req)
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
    signing_key,
    mock_dependencies,
):
    headers = {
        "x-alchemy-signature": sign_request_body(request_body, signing_key),
        "x-forwarded-for": valid_ip,
    }

    if request_body is None:
        req = create_request(None, headers)
    else:
        req = create_request(request_body, headers)

    response = await AlchemyWebhook(req)
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
async def test_servicebus_message(
    create_request,
    valid_ip,
    signing_key,
    request_body,
    expected_messages,
    mock_servicebus,
    mock_dependencies,
):
    headers = {
        "x-alchemy-signature": sign_request_body(request_body, signing_key),
        "x-forwarded-for": valid_ip,
    }

    req = create_request(request_body, headers)

    response = await AlchemyWebhook(req)
    assert response.status_code == 200

    # Assert that ServiceBusClient was initialized with the correct namespace
    mock_servicebus["client"].assert_called_once_with(
        Config.get_servicebus_full_namespace(), ANY, logging_enable=True
    )

    # Assert that ServiceBusClient was initialized with the Credential object
    assert isinstance(mock_servicebus["client"].call_args[0][1], DefaultAzureCredential)

    # Assert that get_topic_sender was called with the correct topic name
    mock_servicebus["instance"].get_topic_sender.assert_called_once_with(
        Config.get_servicebus_topic_name()
    )

    # Assert that send_messages was called
    mock_servicebus["sender"].send_messages.assert_called_once()

    # Retrieve the messages sent
    sent_messages = mock_servicebus["sender"].send_messages.call_args[0][0]

    # Assert the content of the messages
    assert isinstance(sent_messages, list)  # Ensure it's a list of messages
    assert len(sent_messages) == len(expected_messages)

    sent_messages_bodies = [
        json.loads(b"".join(sent_message.body).decode("utf-8").replace("'", '"'))
        for sent_message in sent_messages
    ]

    # Asserting that all messages have been sent as expected, the order doesn't matter because the messages are not sent in order
    assert sorted(sent_messages_bodies, key=lambda x: x["transactionHash"]) == sorted(
        expected_messages, key=lambda x: x["transactionHash"]
    )
