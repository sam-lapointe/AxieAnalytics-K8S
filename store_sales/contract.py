import asyncpg
import logging
import aiohttp
import ast
from asyncpg.exceptions import UniqueViolationError
from datetime import datetime, timezone
from web3 import Web3, AsyncWeb3
from web3.exceptions import Web3ValueError


class ContractNotFoundError(Exception):
    pass


class EventNotFoundError(Exception):
    pass


class RecursionError(Exception):
    pass


class Contract:
    """
    Represents a smart contract and provides methods to interact with it.
    """

    def __init__(
        self,
        conn: asyncpg.Connection,
        w3: AsyncWeb3,
        contract_address: str,
    ):
        self.__eip1967_slot = (
            "0x360894A13BA1A3210667C828492DB98DCA3E2076CC3735A920A3CA505D382BBC"
        )
        self.__conn = conn
        self.__w3 = w3
        self.__contract_address = Web3.to_checksum_address(contract_address)
        self.__name = None
        self.__is_proxy = None
        self.__implementation = None
        self.__abi = None
        self.__contract = None

    @classmethod
    async def create(
        cls,
        conn: asyncpg.Connection,
        w3: AsyncWeb3,
        contract_address: str,
        visited_contracts_addresses: set = None,  # Shared context for recursion tracking
    ):
        """
        Factory method to create and initialize a Contract instance asynchronously.
        """

        if visited_contracts_addresses is None:
            visited_contracts_addresses = set()

        # Check for infinite recursion
        if contract_address in visited_contracts_addresses:
            raise RecursionError(
                f"Infinite recursion detected for contract {contract_address}."
            )
        visited_contracts_addresses.add(contract_address)

        # Create an instance of the class
        instance = cls(conn, w3, contract_address)

        # Perform asynchronous initialization
        async with conn.acquire() as db_connection:
            await instance.__get_contract_data(
                db_connection, visited_contracts_addresses
            )

        return instance

    async def __get_contract_data(
        self, db_connection, visited_contracts_addresses: set
    ) -> None:
        """
        Retrieves the contract data from the database or call __add_contract_data if it isn't in the database.
        It then set the object's variables.
        """
        try:
            # Retrieve contract data from database.
            contract_data = await db_connection.fetchrow(
                "SELECT * FROM contracts WHERE contract_address = $1",
                self.__contract_address,
            )
            if contract_data is None:
                logging.info(
                    f"[__get_contract_data] Contract {self.__contract_address} is not in the database."
                )
                # Call method to retrieve the contract data and add it to the database.
                await self.__add_contract_data(db_connection)
                # Retrieve contract data from database after it has been added.
                contract_data = await db_connection.fetchrow(
                    "SELECT * FROM contracts WHERE contract_address = $1",
                    self.__contract_address,
                )
                if contract_data is None:
                    logging.error(
                        f"[__get_contract_data] Contract {self.__contract_address} is not in the database after calling self.__add_contract_data()."
                    )
                    raise ContractNotFoundError(
                        f"[__get_contract_data] Contract {self.__contract_address} is not in the database after calling self.__add_contract_data()."
                    )

            # Set object variables
            self.__name = contract_data["contract_name"]
            self.__is_proxy = contract_data["is_proxy"]
            self.__abi = ast.literal_eval(contract_data["abi"])
            self.__contract = self.__w3.eth.contract(
                address=self.__contract_address, abi=self.__abi
            )
            implementation_address = contract_data["implementation_address"]

            if self.__is_proxy:
                logging.info(
                    f"[__get_contract_data] Contract {self.__contract_address} ({self.__name}) is a proxy. Fetching implementation contract at {implementation_address}."
                )
                if not implementation_address:
                    raise ValueError(
                        f"[__get_contract_data] Implementation address is missing for proxy contract {self.__contract_address} ({self.__name})."
                    )

                # Create an instance of the implementation contract
                self.__implementation = await Contract.create(
                    self.__conn,
                    self.__w3,
                    implementation_address,
                    visited_contracts_addresses,
                )
        except Exception as e:
            logging.error(f"[__get_contract_data] An unexpected error occured: {e}")
            raise e

    async def __add_contract_data(self, db_connection) -> None:
        """
        Retrieves the contracts information from roninchain.com and adds it to the database.
        """
        try:
            logging.info(
                f"[__add_contract_data] Fetching data for contract {self.__contract_address} from roninchain.com..."
            )

            abi_url = f"https://explorer-kintsugi.roninchain.com/v2/2020/contract/{self.__contract_address}/abi"
            contract_url = f"https://skynet-api.roninchain.com/ronin/explorer/v2/accounts/{self.__contract_address}"

            try:
                # Get contract data from roninchain.com.
                logging.info("Opening aiohttp_ClientSession...")
                async with aiohttp.ClientSession() as http_client:
                    logging.info("ClientSession opened.")
                    async with http_client.get(abi_url) as abi_response:
                        abi_data = await abi_response.json()

                    async with http_client.get(contract_url) as contract_response:
                        contract_data = await contract_response.json()
                        logging.info(contract_data)
                    logging.info("ClientSessionClosed")
            except Exception as e:
                logging.error(
                    f"[__add_contract_data] Error fetching contract data: {e}"
                )
                raise e

            abi = abi_data["result"]["output"]["abi"]

            """
            The contract verifiedName might not be returned depending if it was verified by RoninExplorer.
            """
            try:
                contract_name = contract_data["result"]["contract"]["verifiedName"]
            except KeyError:
                contract_name = "Unnamed"

            """
            This is verifying if the contract is a proxy using the EIP 1967 standard for proxy contracts.
            If the proxy contract was not created using this standard, it will not be detected as a proxy contract.
            """
            implementation_address_raw = await self.__w3.eth.get_storage_at(
                self.__contract_address, self.__eip1967_slot
            )
            if implementation_address_raw.hex() == ("0" * 64):
                is_contract_proxy = False
                implementation_address = None
            else:
                is_contract_proxy = True
                implementation_address = f"0x{implementation_address_raw.hex()[24:]}"

            current_time_utc = datetime.now(timezone.utc)

            contract = {
                "contract_address": self.__contract_address,
                "contract_name": contract_name,
                "abi": str(abi),
                "is_contract_proxy": is_contract_proxy,
                "implementation_address": implementation_address,
                "created_at": current_time_utc,
                "modified_at": current_time_utc,
            }

            # Add the contract to the database.
            logging.info(
                f"[__add_contract_data] Adding contract {self.__contract_address} ({contract_name}) to the database..."
            )
            try:
                await db_connection.execute(
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
                    *contract.values(),
                )
                logging.info(
                    f"[__add_contract_data] Successfully added contract {self.__contract_address} ({contract_name}) to the database."
                )
            except UniqueViolationError:
                logging.info(
                    f"[__add_contract_data] Contract {self.__contract_address} is already in the database. Skipped."
                )

        except Exception as e:
            logging.error(
                f"[__add_contract_data] An unexpected error occured while retrieving contract {self.__contract_address} or adding it to the database: {e}"
            )
            raise e

    def get_contract_address(self) -> str:
        return self.__contract_address

    def get_event_name(self, topic: str) -> str:
        """
        Returns the event name using the topic.
        """
        try:
            logging.info(f"[get_event_data] Retrieving event name for topic {topic}...")
            if self.__is_proxy:
                logging.info(
                    f"[get_event_name] Successfuly returned event name for topic {topic}."
                )
                return self.__implementation.get_event_name(topic)
            else:
                logging.info(
                    f"[get_event_name] Successfuly returned event name for topic {topic}."
                )
                return self.__contract.get_event_by_topic(topic).name
        except Web3ValueError as e:
            logging.error(
                f"[get_event_name] Could not find any event matching this topic: {topic}"
            )
            raise e

    def get_event_data(self, topic: str, log: dict) -> dict:
        """
        Returns the decoded log data in a dictionnary.
        """
        logging.info(f"[get_event_data] Retrieving event data for topic {topic}...")
        event_name = self.get_event_name(topic)

        if self.__is_proxy:
            event_class = getattr(self.__implementation.__contract.events, event_name)
        else:
            event_class = getattr(self.__contract.events, event_name)

        logging.info(
            f"[get_event_data] Successfuly returned event data for topic {topic}."
        )
        return event_class.process_log(log)

    def get_event_signature_hash(self, event_name) -> str:
        if self.__is_proxy:
            logging.info(
                f"[get_event_signature_hash] Retrieving signature hash for {event_name} event in contract {self.__implementation.__contract_address} ({self.__implementation.__name})"
            )
            event_signature = self.__implementation.__contract.find_events_by_name(
                event_name
            )
            if not event_signature:
                logging.error(
                    f"[get_event_signature_hash] The '{event_name}' event was not found in the implementation contract {self.__implementation.__contract_address} ({self.__implementation.__name})."
                )
                raise EventNotFoundError(
                    f"The '{event_name}' event was not found in the implementation contract {self.__implementation.__contract_address} ({self.__implementation.__name})."
                )
        else:
            logging.info(
                f"[get_event_signature_hash] Retrieving signature hash for {event_name} event in contract {self.__contract_address} ({self.__name})"
            )
            event_signature = self.__contract.find_events_by_name(event_name)
            if not event_signature:
                logging.error(
                    f"[get_event_signature_hash] The '{event_name}' event was not found in the contract {self.__contract_address} ({self.__name})."
                )
                raise EventNotFoundError(
                    f"The '{event_name}' event was not found in the contract {self.__contract_address} ({self.__name})."
                )

        return event_signature[0].topic
