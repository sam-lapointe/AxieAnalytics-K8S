import pytest
import sys
from pathlib import Path
from web3 import Web3
from web3.datastructures import AttributeDict
from hexbytes import HexBytes


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from transaction import Transaction
from contract import Contract


@pytest.fixture
def conn(mocker):
    return mocker.AsyncMock()


@pytest.fixture
def w3(mocker):
    return mocker.AsyncMock()


@pytest.fixture
def transaction_hash():
    return "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"


@pytest.fixture
def transaction_receipt():
    return AttributeDict(
        {
            "blockHash": HexBytes(
                "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
            ),
            "blockNumber": 44153279,
            "contractAddress": None,
            "cumulativeGasUsed": 523582,
            "effectiveGasPrice": 21072619952,
            "from": "0xf536Ba5D2Ba5F24fb35d8C9Ee256753A5Ae3D0c5",
            "gasUsed": 330242,
            "logs": [
                AttributeDict(
                    {
                        "address": "0xc99a6A985eD2Cac1ef41640596C5A5f9F4E19Ef5",
                        "topics": [
                            HexBytes(
                                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                            ),
                            HexBytes(
                                "0x000000000000000000000000f536ba5d2ba5f24fb35d8c9ee256753a5ae3d0c5"
                            ),
                            HexBytes(
                                "0x000000000000000000000000fff9ce5f71ca6178d3beecedb61e7eff1602950e"
                            ),
                        ],
                        "data": HexBytes(
                            "0x00000000000000000000000000000000000000000000000000068651d432bc02"
                        ),
                        "blockNumber": 44153279,
                        "transactionHash": HexBytes(
                            "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                        ),
                        "transactionIndex": 1,
                        "blockHash": HexBytes(
                            "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
                        ),
                        "logIndex": 2,
                        "removed": False,
                    }
                ),
                AttributeDict(
                    {
                        "address": "0xc99a6A985eD2Cac1ef41640596C5A5f9F4E19Ef5",
                        "topics": [
                            HexBytes(
                                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                            ),
                            HexBytes(
                                "0x000000000000000000000000fff9ce5f71ca6178d3beecedb61e7eff1602950e"
                            ),
                            HexBytes(
                                "0x000000000000000000000000245db945c485b68fdc429e4f7085a1761aa4d45d"
                            ),
                        ],
                        "data": HexBytes(
                            "0x000000000000000000000000000000000000000000000000000046fd13e5ff07"
                        ),
                        "blockNumber": 44153279,
                        "transactionHash": HexBytes(
                            "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                        ),
                        "transactionIndex": 1,
                        "blockHash": HexBytes(
                            "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
                        ),
                        "logIndex": 3,
                        "removed": False,
                    }
                ),
                AttributeDict(
                    {
                        "address": "0xc99a6A985eD2Cac1ef41640596C5A5f9F4E19Ef5",
                        "topics": [
                            HexBytes(
                                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                            ),
                            HexBytes(
                                "0x000000000000000000000000fff9ce5f71ca6178d3beecedb61e7eff1602950e"
                            ),
                            HexBytes(
                                "0x000000000000000000000000094300dacf0eed244664e326d27406f0b90b8809"
                            ),
                        ],
                        "data": HexBytes(
                            "0x00000000000000000000000000000000000000000000000000063f54c04cbcfb"
                        ),
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
                ),
                AttributeDict(
                    {
                        "address": "0x32950db2a7164aE833121501C797D79E7B79d74C",
                        "topics": [
                            HexBytes(
                                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                            ),
                            HexBytes(
                                "0x000000000000000000000000094300dacf0eed244664e326d27406f0b90b8809"
                            ),
                            HexBytes(
                                "0x000000000000000000000000f536ba5d2ba5f24fb35d8c9ee256753a5ae3d0c5"
                            ),
                            HexBytes(
                                "0x0000000000000000000000000000000000000000000000000000000000b1c082"
                            ),
                        ],
                        "data": HexBytes("0x"),
                        "blockNumber": 44153279,
                        "transactionHash": HexBytes(
                            "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                        ),
                        "transactionIndex": 1,
                        "blockHash": HexBytes(
                            "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
                        ),
                        "logIndex": 5,
                        "removed": False,
                    }
                ),
                AttributeDict(
                    {
                        "address": "0x32950db2a7164aE833121501C797D79E7B79d74C",
                        "topics": [
                            HexBytes(
                                "0xcc2c68164f9f7f0c063ba98bcf89498c0f3f5e3acc32bf4ab46195ecb489c13b"
                            ),
                            HexBytes(
                                "0x0000000000000000000000000000000000000000000000000000000000b1c082"
                            ),
                            HexBytes(
                                "0x0000000000000000000000000000000000000000000000000000000000000023"
                            ),
                        ],
                        "data": HexBytes("0x"),
                        "blockNumber": 44153279,
                        "transactionHash": HexBytes(
                            "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                        ),
                        "transactionIndex": 1,
                        "blockHash": HexBytes(
                            "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
                        ),
                        "logIndex": 6,
                        "removed": False,
                    }
                ),
                AttributeDict(
                    {
                        "address": "0xffF9Ce5f71ca6178D3BEEcEDB61e7Eff1602950E",
                        "topics": [
                            HexBytes(
                                "0x968d1942d9971cb9c45c722957d854c38f327206399d12ae49ca2f9c5dd06fda"
                            ),
                        ],
                        "data": HexBytes(
                            "0x00000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000686a3238e07ef000000000000000000000000c99a6a985ed2cac1ef41640596c5a5f9f4e19ef5000000000000000000000000f536ba5d2ba5f24fb35d8c9ee256753a5ae3d0c500000000000000000000000000000000000000000000000000068651d432bc0200000000000000000000000000000000000000000000000000000000000003c000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000068651d432bc0200000000000000000000000000000000000000000000000000000000000002e0000000000000000000000000f536ba5d2ba5f24fb35d8c9ee256753a5ae3d0c5000000000000000000000000f536ba5d2ba5f24fb35d8c9ee256753a5ae3d0c5000000000000000000000000094300dacf0eed244664e326d27406f0b90b8809000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000001a00000000000000000000000000000000000000000000000000000000067f8c97d000000000000000000000000c99a6a985ed2cac1ef41640596c5a5f9f4e19ef50000000000000000000000000000000000000000000000000000000067f7f68d0000000000000000000000000000000000000000000000000006abb52d0913e80000000000000000000000000000000000000000000000000000000067f8c97d0000000000000000000000000000000000000000000000000005ccf6967732b400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c7824e2cbf387946ffb482282029bb9562bc763fda7690fe3f3ea712ec88951300000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000032950db2a7164ae833121501c797d79e7b79d74c0000000000000000000000000000000000000000000000000000000000b1c0820000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000008417ac6838be147ab0e201496b2e5edf90a48cc50000000000000000000000008417ac6838be147ab0e201496b2e5edf90a48cc5000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000245db945c485b68fdc429e4f7085a1761aa4d45d000000000000000000000000245db945c485b68fdc429e4f7085a1761aa4d45d00000000000000000000000000000000000000000000000000000000000001a9000000000000000000000000000000000000000000000000000046fd13e5ff07000000000000000000000000000000000000000000000000000000000000000200000000000000000000000022cefc91e9b7c0f3890ebf9527ea89053490694e00000000000000000000000022cefc91e9b7c0f3890ebf9527ea89053490694e000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000094300dacf0eed244664e326d27406f0b90b8809000000000000000000000000094300dacf0eed244664e326d27406f0b90b8809000000000000000000000000000000000000000000000000000000000000256700000000000000000000000000000000000000000000000000063f54c04cbcfb"
                        ),
                        "blockNumber": 44153279,
                        "transactionHash": HexBytes(
                            "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                        ),
                        "transactionIndex": 1,
                        "blockHash": HexBytes(
                            "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
                        ),
                        "logIndex": 7,
                        "removed": False,
                    }
                ),
            ],
            "logsBloom": HexBytes(
                "0x0000000010000000040000000000000000000000000000000000000000000000800010000000000000008000000000000000000010000080000000000000000800000000000000000000002802100000080000000000000000000000000000000000000000100000000000000000000000000000000000000000001000000000000000000400000000000000000090008000000020020000000000000010000010000000000000000000000000000000000100000000000000020000000000000000000200000000000200000000000000000000000000000000000000000000000000800400001000001000000000000000a000000000000020000400040000"
            ),
            "status": 1,
            "to": "0xffF9Ce5f71ca6178D3BEEcEDB61e7Eff1602950E",
            "transactionHash": HexBytes(
                "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
            ),
            "transactionIndex": 1,
            "type": 2,
        }
    )


# Test the Transaction.__get_receipt method.
@pytest.mark.asyncio
async def test_get_receipt(mocker, conn, w3, transaction_hash):
    # Mock eth.get_transaction_receipt
    w3.eth.get_transaction_receipt = mocker.AsyncMock()

    # Create a Transaction instance
    transaction = Transaction(conn, w3)

    # Call the method
    await transaction._Transaction__get_receipt(transaction_hash)
    w3.eth.get_transaction_receipt.assert_called_once_with(transaction_hash)


# Test the Transaction.process_logs method.
@pytest.mark.asyncio
async def test_process_logs(mocker, conn, w3, transaction_hash, transaction_receipt):
    # Mock AsyncWeb3.eth.get_transaction_receipt method
    w3.eth.get_transaction_receipt = mocker.AsyncMock(return_value=transaction_receipt)

    # Mock Contract.create method
    mock_weth_contract = mocker.MagicMock()
    mock_weth_contract.get_contract_address.return_value = Web3.to_checksum_address(
        "0xc99a6a985ed2cac1ef41640596c5a5f9f4e19ef5"
    )
    mock_weth_contract.get_event_signature_hash.return_value = (
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    )
    mock_weth_contract.get_event_data.side_effect = [
        AttributeDict(
            {
                "args": AttributeDict(
                    {
                        "_from": "0xf536Ba5D2Ba5F24fb35d8C9Ee256753A5Ae3D0c5",
                        "_to": "0xffF9Ce5f71ca6178D3BEEcEDB61e7Eff1602950E",
                        "_value": 1836535870831618,
                    }
                ),
                "event": "Transfer",
                "logIndex": 2,
                "transactionIndex": 1,
                "transactionHash": HexBytes(
                    "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                ),
                "address": "0xc99a6A985eD2Cac1ef41640596C5A5f9F4E19Ef5",
                "blockHash": HexBytes(
                    "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
                ),
                "blockNumber": 44153279,
            }
        ),
        AttributeDict(
            {
                "args": AttributeDict(
                    {
                        "_from": "0xffF9Ce5f71ca6178D3BEEcEDB61e7Eff1602950E",
                        "_to": "0x245db945c485b68fDc429E4F7085a1761Aa4d45d",
                        "_value": 78052774510343,
                    }
                ),
                "event": "Transfer",
                "logIndex": 3,
                "transactionIndex": 1,
                "transactionHash": HexBytes(
                    "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                ),
                "address": "0xc99a6A985eD2Cac1ef41640596C5A5f9F4E19Ef5",
                "blockHash": HexBytes(
                    "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
                ),
                "blockNumber": 44153279,
            }
        ),
        AttributeDict(
            {
                "args": AttributeDict(
                    {
                        "_from": "0xffF9Ce5f71ca6178D3BEEcEDB61e7Eff1602950E",
                        "_to": "0x094300DacF0eED244664e326d27406F0B90b8809",
                        "_value": 1758483096321275,
                    }
                ),
                "event": "Transfer",
                "logIndex": 4,
                "transactionIndex": 1,
                "transactionHash": HexBytes(
                    "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                ),
                "address": "0xc99a6A985eD2Cac1ef41640596C5A5f9F4E19Ef5",
                "blockHash": HexBytes(
                    "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
                ),
                "blockNumber": 44153279,
            }
        ),
    ]

    mock_axie_contract = mocker.MagicMock()
    mock_axie_contract.get_contract_address.return_value = Web3.to_checksum_address(
        "0x32950db2a7164ae833121501c797d79e7b79d74c"
    )
    mock_axie_contract.get_event_signature_hash.return_value = (
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    )
    mock_axie_contract.get_event_data.side_effect = [
        AttributeDict(
            {
                "args": AttributeDict(
                    {
                        "_from": "0x094300DacF0eED244664e326d27406F0B90b8809",
                        "_to": "0xf536Ba5D2Ba5F24fb35d8C9Ee256753A5Ae3D0c5",
                        "_tokenId": 11649154,
                    }
                ),
                "event": "Transfer",
                "logIndex": 5,
                "transactionIndex": 1,
                "transactionHash": HexBytes(
                    "0xb05e64ab435371a5c4b6e23f416a37fec881419228db0e35d9b3549204f549eb"
                ),
                "address": "0x32950db2a7164aE833121501C797D79E7B79d74C",
                "blockHash": HexBytes(
                    "0xf95b5c3227fc15c4c882f8287b490b99e629dc31dd015da2b7a9d6d4b0ee0f93"
                ),
                "blockNumber": 44153279,
            }
        )
    ]

    mocker.patch.object(
        Contract, "create", side_effect=[mock_weth_contract, mock_axie_contract]
    )

    # Create a Transaction instance
    transaction = Transaction(conn, w3)

    # Call process_logs method
    sales_list = await transaction.process_logs(transaction_hash)

    # Assert the sales_list is correct
    assert sales_list == [
        {"price_weth": 0.001836535870831618, "axie_id": 11649154},
    ]

    # Assert the calls to the mock contracts
    w3.eth.get_transaction_receipt.assert_called_once_with(transaction_hash)
    mock_weth_contract.get_event_data.call_count == 3
    mock_axie_contract.get_event_data.assert_called_once()
