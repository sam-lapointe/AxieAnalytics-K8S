import pytest
import sys
import asyncpg
import json
from pathlib import Path
from web3 import Web3
from web3.exceptions import Web3ValueError
from web3.datastructures import AttributeDict
from hexbytes import HexBytes

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contract import (
    datetime,
    timezone,
    Contract,
    ContractNotFoundError,
    EventNotFoundError,
    RecursionError,
)


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


# Mock the Web3 instance.
@pytest.fixture
def w3(mocker):
    return mocker.AsyncMock()


@pytest.fixture
def abi():
    return json.dumps(
        [
            {
                "anonymous": False,
                "inputs": [
                    {
                        "indexed": True,
                        "internalType": "address",
                        "name": "_from",
                        "type": "address",
                    },
                    {
                        "indexed": True,
                        "internalType": "address",
                        "name": "_to",
                        "type": "address",
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "_value",
                        "type": "uint256",
                    },
                ],
                "name": "Transfer",
                "type": "event",
            }
        ]
    )


# Test the Contract.create method.
@pytest.mark.parametrize(
    "contract_address, visited_addresses",
    [
        ("0x1234567890abcdef1234567890abcdef12345678", None),
        (
            "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            set("0x1234567890abcdef1234567890abcdef12345678"),
        ),
        (
            "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            set("0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"),
        ),
    ],
)
@pytest.mark.asyncio
async def test_create(mocker, conn, w3, contract_address, visited_addresses):
    mocker.patch("contract.Contract._Contract__get_contract_data", return_value=None)

    if visited_addresses == contract_address:
        with pytest.raises(RecursionError):
            Contract.create(conn, w3, contract_address, visited_addresses)
    elif visited_addresses is None:
        contract = await Contract.create(conn, w3, contract_address, visited_addresses)
        assert contract is not None
        assert isinstance(contract, Contract)


# Test the Contract.__get_contract_data method when the contract exists in the database.
@pytest.mark.asyncio
async def test_get_contract_data_exists_in_db(mocker, conn, w3):
    # Mock the database fetchrow method to return the proxy and implementation contract data.
    db_connection = await conn.acquire().__aenter__()
    db_connection.fetchrow.side_effect = [
        {
            "contract_name": "ProxyContract",
            "is_proxy": True,
            "abi": "[]",
            "implementation_address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        },
        {
            "contract_name": "ImplementationContract",
            "is_proxy": False,
            "abi": "[]",
            "implementation_address": None,
        },
    ]

    # Create contract instance.
    contract = await Contract.create(
        conn, w3, "0x1234567890abcdef1234567890abcdef12345678", None
    )

    assert contract._Contract__name == "ProxyContract"
    assert contract._Contract__is_proxy  # True
    assert contract._Contract__abi == []
    assert contract._Contract__contract_address == Web3.to_checksum_address(
        "0x1234567890abcdef1234567890abcdef12345678"
    )
    assert isinstance(contract._Contract__implementation, Contract)
    assert (
        contract._Contract__implementation._Contract__name == "ImplementationContract"
    )
    assert not contract._Contract__implementation._Contract__is_proxy  # False
    assert contract._Contract__implementation._Contract__abi == []
    assert contract._Contract__implementation._Contract__implementation is None
    assert (
        contract._Contract__implementation._Contract__contract_address
        == Web3.to_checksum_address("0xabcdefabcdefabcdefabcdefabcdefabcdefabcd")
    )


# Test the Contract.__get_contract_data method when the contract does not exist in the database.
@pytest.mark.asyncio
async def test_get_contract_data_not_in_db(mocker, conn, w3):
    # Mock database fetchrow to return None initially and then the contract data.
    db_connection = await conn.acquire().__aenter__()
    db_connection.fetchrow.side_effect = [
        None,
        {
            "contract_name": "TestContract",
            "is_proxy": False,
            "abi": "[]",
            "implementation_address": None,
        },
    ]

    # Mock __add_contract_data.
    mocker.patch.object(
        Contract, "_Contract__add_contract_data", new_callable=mocker.AsyncMock
    )

    # Create contract instance.
    contract = await Contract.create(
        conn, w3, "0x1234567890abcdef1234567890abcdef12345678", None
    )

    assert contract._Contract__name == "TestContract"
    assert not contract._Contract__is_proxy  # False
    assert contract._Contract__abi == []
    assert contract._Contract__implementation is None
    assert contract._Contract__contract_address == Web3.to_checksum_address(
        "0x1234567890abcdef1234567890abcdef12345678"
    )

    contract._Contract__add_contract_data.assert_called_once()
    assert db_connection.fetchrow.call_count == 2


# Test the Contract.__get_contract_data method when the contract is not found in the database after it was added to the database.
@pytest.mark.asyncio
async def test_get_contract_data_missing_after_add(mocker, conn, w3):
    # Mock database fetchrow to return None two times.
    db_connection = await conn.acquire().__aenter__()
    db_connection.fetchrow.side_effect = [None, None]

    # Mock __add_contract_data.
    mocker.patch.object(
        Contract, "_Contract__add_contract_data", new_callable=mocker.AsyncMock
    )

    # Create contract instance.
    with pytest.raises(ContractNotFoundError):
        contract = await Contract.create(
            conn, w3, "0x1234567890abcdef1234567890abcdef12345678", None
        )
        contract._Contract__add_contract_data.assert_called_once()

    assert db_connection.fetchrow.call_count == 2


# Test the Contract.__add_contract_data method.
@pytest.mark.parametrize(
    "is_new_contract",
    [
        True,
        False,
    ],
)
@pytest.mark.asyncio
async def test_add_contract_data(mocker, conn, w3, is_new_contract):
    # Mock the current time.
    mock_current_time = datetime(2025, 5, 9, 12, 0, 0, tzinfo=timezone.utc)
    mock_datetime = mocker.patch("contract.datetime")
    mock_datetime.now.return_value = mock_current_time

    # Mock HTTP session and responses.
    mock_http_session = mocker.patch("aiohttp.ClientSession")
    mock_http_client_instance = mock_http_session.return_value
    mock_http_client_instance.__aenter__.return_value = mock_http_client_instance
    mock_http_client_instance.__aexit__.return_value = None

    mock_abi_response = mocker.AsyncMock()
    mock_abi_response.__aenter__.return_value.json.return_value = {
        "result": {"output": {"abi": []}}
    }

    mock_contract_response = mocker.AsyncMock()
    mock_contract_response.__aenter__.return_value.json.return_value = {
        "result": {
            "contract": {
                "verifiedName": "TestContract",
            }
        }
    }

    mock_http_client_instance.__aenter__.return_value.get.side_effect = [
        mock_abi_response,
        mock_contract_response,
    ]

    # Mock get_storage_at to return a valid bytes object.
    w3.eth.get_storage_at = mocker.AsyncMock(
        return_value=bytes.fromhex(
            "000000000000000000000000abcdefabcdefabcdefabcdefabcdefabcdefabcd"
        )
    )

    contract = Contract(conn, w3, "0x1234567890abcdef1234567890abcdef12345678")

    if is_new_contract:
        await contract._Contract__add_contract_data(conn)

        contract_data = {
            "contract_address": contract._Contract__contract_address,
            "contract_name": "TestContract",
            "abi": "[]",
            "is_contract_proxy": True,
            "implementation_address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "created_at": mock_current_time,
            "modified_at": mock_current_time,
        }

        # The indentation of the query string is important to match the expected format.
        conn.execute.assert_called_once_with(
                    """
                    INSERT INTO contracts(
                        contract_address,
                        contract_name,
                        abi,
                        is_proxy,
                        implementation_address,
                        created_at,
                        modified_at                      
                    )
                    VALUES (
                        $1, $2, $3, $4, $5, $6, $7
                    )
                    """,
            *contract_data.values(),
        )
    else:
        # Mock conn.execute to raise a unique violation error
        conn.execute.side_effect = asyncpg.exceptions.UniqueViolationError(
            "Unique violation error"
        )

        # No errors should be raised because this error is handled in the __add_contract_data method.
        contract = Contract(conn, w3, "0x1234567890abcdef1234567890abcdef12345678")
        await contract._Contract__add_contract_data(conn)

        conn.execute.assert_called_once()


# Test the Contract.get_contract_address method.
@pytest.mark.parametrize(
    "contract_address",
    [
        ("0x1234567890abcdef1234567890abcdef12345678"),
        ("0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"),
    ],
)
@pytest.mark.asyncio
async def test_get_contract_address(mocker, conn, w3, contract_address):
    # Mock the contract.
    contract = Contract(conn, w3, contract_address)

    returned_contract_address = contract.get_contract_address()
    assert returned_contract_address == Web3.to_checksum_address(contract_address)


# Test the Contract.get_event_name method.
@pytest.mark.parametrize(
    "topic_hash,expected_event_name",
    [
        (
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "Transfer",
        ),
        (
            "0x8c5be1e5ebec7d5bd14f71443d9b2b6e3d3e8e8e8e8e8e8e8e8e8e8e8e8e8e8",
            "Approval",
        ),
    ],
)
def test_get_event_name(mocker, abi, topic_hash, expected_event_name):
    # Mock the proxy contract and dependencies.
    conn = mocker.Mock()
    w3 = Web3()
    proxy_contract = Contract(conn, w3, "0x1234567890abcdef1234567890abcdef12345678")
    proxy_contract._Contract__is_proxy = True

    # Mock the implementation contract.
    implementation_contract = Contract(
        conn, w3, "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    )
    implementation_contract._Contract__is_proxy = False
    implementation_contract._Contract__abi = abi

    # Mock Web3 contract for the implementation contract.
    implementation_contract._Contract__contract = (
        implementation_contract._Contract__w3.eth.contract(
            address=implementation_contract._Contract__contract_address,
            abi=implementation_contract._Contract__abi,
        )
    )

    # Set the implementation contract in the proxy contract.
    proxy_contract._Contract__implementation = implementation_contract

    if expected_event_name == "Transfer":
        event_name = proxy_contract.get_event_name(topic_hash)
        assert event_name == expected_event_name
    else:
        with pytest.raises(Web3ValueError):
            proxy_contract.get_event_name(topic_hash)


# Test the Contract.get_event_data method.
def test_get_event_data(mocker, abi):
    # Mock the proxy contract and dependencies.
    conn = mocker.Mock()
    w3 = Web3()
    proxy_contract = Contract(conn, w3, "0x1234567890abcdef1234567890abcdef12345678")
    proxy_contract._Contract__is_proxy = True

    # Mock the implementation contract.
    implementation_contract = Contract(
        conn, w3, "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    )
    implementation_contract._Contract__is_proxy = False
    implementation_contract._Contract__abi = abi

    # Mock Web3 contract for the implementation contract.
    implementation_contract._Contract__contract = (
        implementation_contract._Contract__w3.eth.contract(
            address=implementation_contract._Contract__contract_address,
            abi=implementation_contract._Contract__abi,
        )
    )

    # Set the implementation contract in the proxy contract.
    proxy_contract._Contract__implementation = implementation_contract

    # Mock the log data.
    log_data = AttributeDict(
        {
            "address": "0xc99a6A985eD2Cac1ef41640596C5A5f9F4E19Ef5",
            "topics": [
                HexBytes(
                    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                ),
                HexBytes(
                    "0x000000000000000000000000fff9ce5f71ca6178d3beecedb61e7eff1602950e"
                ),  # _from
                HexBytes(
                    "0x000000000000000000000000094300dacf0eed244664e326d27406f0b90b8809"
                ),  # _to
            ],
            "data": HexBytes(
                "0x00000000000000000000000000000000000000000000000000063f54c04cbcfb"
            ),  # _value
            "blockNumber": 44153279,
            "transactionHash": HexBytes(
                "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
            ),
            "transactionIndex": 1,
            "blockHash": HexBytes(
                "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
            ),
            "logIndex": 4,
            "removed": False,
        }
    )

    # Call get_event_data method.
    transfer_topic_hash = (
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    )
    event_data_result = proxy_contract.get_event_data(transfer_topic_hash, log_data)
    print(event_data_result)

    assert (
        event_data_result["args"]["_from"]
        == "0xffF9Ce5f71ca6178D3BEEcEDB61e7Eff1602950E"
    )
    assert (
        event_data_result["args"]["_to"] == "0x094300DacF0eED244664e326d27406F0B90b8809"
    )
    assert event_data_result["args"]["_value"] == 1758483096321275


# Test the Contract.get_event_signature_hash method.
@pytest.mark.parametrize(
    "event_name,expected_signature_hash",
    [
        (
            "Transfer",
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        ),
        ("Approval", None),
    ],
)
def test_get_event_signature_hash(mocker, abi, event_name, expected_signature_hash):
    # Mock the proxy contract and dependencies.
    conn = mocker.Mock()
    w3 = Web3()
    proxy_contract = Contract(conn, w3, "0x1234567890abcdef1234567890abcdef12345678")
    proxy_contract._Contract__is_proxy = True

    # Mock the implementation contract.
    implementation_contract = Contract(
        conn, w3, "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    )
    implementation_contract._Contract__is_proxy = False
    implementation_contract._Contract__abi = abi

    # Mock Web3 contract for the implementation contract.
    implementation_contract._Contract__contract = (
        implementation_contract._Contract__w3.eth.contract(
            address=implementation_contract._Contract__contract_address,
            abi=implementation_contract._Contract__abi,
        )
    )

    # Set the implementation contract in the proxy contract.
    proxy_contract._Contract__implementation = implementation_contract

    # Call get_event_signature_hash method.
    if event_name == "Transfer":
        event_signature_hash_result = proxy_contract.get_event_signature_hash(
            event_name
        )
        assert event_signature_hash_result == expected_signature_hash
    else:
        with pytest.raises(EventNotFoundError):
            proxy_contract.get_event_signature_hash(event_name)
