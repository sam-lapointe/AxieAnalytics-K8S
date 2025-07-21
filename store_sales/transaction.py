import asyncpg
import logging
from contract import Contract
from web3 import Web3, AsyncWeb3


class Transaction:
    """
    Represents a Ronin blockchain sale transaction and interacts with associated contracts to gather specific data about the sale.
    """

    def __init__(
        self,
        conn: asyncpg.Connection,
        w3: AsyncWeb3,
    ):
        self.__conn = conn
        self.__w3 = w3

    async def __get_receipt(self, transaction_hash) -> dict:
        """Returns the transaction receipt."""
        try:
            receipt = await self.__w3.eth.get_transaction_receipt(transaction_hash)
            return receipt

        except Exception as e:
            logging.error(
                f"[__get_receipt] An unexpected error occured while retrieving receipt for transaction {transaction_hash}: {e}"
            )
            raise e

    async def process_logs(self, transaction_hash) -> list:
        """
        Looks for specifc data in the logs and returns a list of the sold prices and assets IDs.
        """
        try:
            logging.info(
                f"[process_logs] Processing logs for transaction {transaction_hash}..."
            )
            receipt = await self.__get_receipt(transaction_hash)
            logs = receipt["logs"]
            recipient = receipt["to"]

            weth_contract = await Contract.create(
                self.__conn,
                self.__w3,
                "0xc99a6a985ed2cac1ef41640596c5a5f9f4e19ef5",
            )
            weth_contract_address = weth_contract.get_contract_address()
            weth_transfer_signature_hash = weth_contract.get_event_signature_hash(
                "Transfer"
            )

            axie_proxy_contract = await Contract.create(
                self.__conn,
                self.__w3,
                "0x32950db2a7164ae833121501c797d79e7b79d74c",
            )
            axie_proxy_contract_address = axie_proxy_contract.get_contract_address()
            axie_transfer_signature_hash = axie_proxy_contract.get_event_signature_hash(
                "Transfer"
            )

            prices = []
            axies = []

            for log in logs:
                logging.info(
                    f"[process_logs] Log Contract Address: {Web3.to_checksum_address(log['address'])}, Topic Event: 0x{log['topics'][0].hex()}"
                )
                topic = f"0x{log['topics'][0].hex()}"

                if (
                    Web3.to_checksum_address(log["address"]) == weth_contract_address
                    and topic == weth_transfer_signature_hash
                ):
                    """
                    Every payment is converted into WETH and transferred to the contract (recipient).
                    If the payment was made directly in WETH, the WETH is transfered from the sender directly to the contract (recipient).

                    Else, the sender transfer the currency to the contract, which then proceeds to exchange it for WETH.
                    This causes multiple events, the important one is a transfer from the WETH contract to the contract (recipient).
                    """
                    logging.info("[process_logs] Retrieving data for WETH transfer...")
                    event_data = weth_contract.get_event_data(topic, log)
                    if event_data["args"]["_to"] == recipient:
                        if len(prices) > len(axies):
                            # This make sure that the last price is removed if no asset was found for that sale.
                            prices.pop()

                        weth_value = Web3.from_wei(
                            event_data["args"]["_value"], "ether"
                        )
                        prices.append(float(weth_value))
                        logging.info(
                            f"[process_logs] Found WETH transfer going to the recipient of the transaction. Added WETH value of {weth_value} to list of prices."
                        )
                elif (
                    Web3.to_checksum_address(log["address"])
                    == axie_proxy_contract_address
                    and topic == axie_transfer_signature_hash
                ):
                    """
                    Every Axie sales call the Axie Proxy contract with the event Transfer to transfer the Axie from the seller to buyer.
                    """
                    event_data = axie_proxy_contract.get_event_data(topic, log)
                    axie_id = event_data["args"]["_tokenId"]
                    axies.append(axie_id)
                    logging.info(
                        f"[process_logs] Found Axie transfer. Added Axie {axie_id} to the list of axies."
                    )

            if len(prices) > len(axies):
                # This make sure that the last price is removed if no asset was found for that sale.
                prices.pop()

            """
            All events in a transaction are in the same order wheter it contains multiple sales or only one.
            First there is the currency transfer and swaps if needed, then the asset transfer and it is repeated 
            in this order if there are many sales   in the transaction.
            """
            sales_list = [
                {"price_weth": price, "axie_id": axie_id}
                for price, axie_id in zip(prices, axies)
            ]
            logging.info(f"[process_logs] Prices List: {prices}")
            logging.info(f"[process_logs] Axies List: {axies}")
            logging.info(f"[process_logs] Sales List: {sales_list}")
            return sales_list

        except Exception as e:
            logging.error(
                f"[process_logs] An unexpected error occured while processing logs for transaction {transaction_hash}: {e}"
            )
            raise e
