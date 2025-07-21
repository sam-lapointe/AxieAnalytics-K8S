import azure.functions as func
import logging
import hmac
import hashlib
from azure.keyvault.secrets.aio import SecretClient
from azure.identity.aio import DefaultAzureCredential
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from config import Config


# Authenticate to Azure
credential = DefaultAzureCredential()
key_vault_client = SecretClient(Config.get_key_vault_url(), credential)


# Alchemy signing key to validate the signature
SIGNING_KEY = None


# Asynchronous function to retrieve the signing key.
async def get_signing_key():
    global SIGNING_KEY
    if SIGNING_KEY is None:
        try:
            secret_name = Config.get_signing_key_name()
            secret = await key_vault_client.get_secret(secret_name)
            SIGNING_KEY = secret.value
            logging.info("Successfully retrieved the signing key.")
        except Exception as e:
            logging.error(f"Failed to retrieve signing key: {e}")
            raise
    return SIGNING_KEY


# Application initialization
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# Helper function to validate the signature
def is_valid_signature_for_string_body(
    body: str, signature: str, signing_key: str
) -> bool:
    digest = hmac.new(
        bytes(signing_key, "utf-8"),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return signature == digest


@app.route(route="webhook")
async def AlchemyWebhook(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # Retrieve the signing key asynchronously
    try:
        signing_key = await get_signing_key()
    except Exception as e:
        logging.critical(f"Failed to retrieve signing key: {e}")
        return func.HttpResponse(status_code=500)

    source_ip = req.headers.get("x-forwarded-for")
    # Verifies if the request is coming from an authorized IP address
    authorized_ips = Config.get_authorized_ips()
    if source_ip not in authorized_ips and len(authorized_ips) != 0:
        logging.error(f"Request coming from unauthorized IP address: {source_ip}")
        return func.HttpResponse(status_code=403)

    signature = req.headers.get("x-alchemy-signature")
    # Verify if the Alchemy signature is in the header
    if not signature:
        logging.error("Missing signature in headers.")
        return func.HttpResponse(status_code=400)

    # Get the body content
    try:
        req_body = req.get_json()
        logging.info(f"Body Size: {len(bytes(str(req_body), 'utf-8'))} bytes")
    except ValueError:
        logging.error("Missing body.")
        return func.HttpResponse(status_code=400)
    except Exception as e:
        logging.error(f"Unknown error with the request body: {e}")
        return func.HttpResponse(status_code=400)

    # Verify if the signature is valid
    if not is_valid_signature_for_string_body(req.get_body(), signature, signing_key):
        logging.error("The signature is invalid.")
        return func.HttpResponse(status_code=401)

    # Verify is there is a body to the request
    if not req_body:
        logging.error("Missing body.")
        return func.HttpResponse(status_code=400)

    # Loop throuh reveived transactions and send a message to Azure Service Bus Topic for every transaction
    try:
        logs = req_body["event"]["data"]["block"]["logs"]
        # Create a list of unique transaction hash
        transactions = set([log["transaction"]["hash"] for log in logs])
        async with ServiceBusClient(
            Config.get_servicebus_full_namespace(), credential, logging_enable=True
        ) as servicebus_client:
            async with servicebus_client.get_topic_sender(
                Config.get_servicebus_topic_name()
            ) as sender:
                # Prepare all messages
                messages = [
                    ServiceBusMessage(
                        str(
                            {
                                "blockNumber": req_body["event"]["data"]["block"][
                                    "number"
                                ],
                                "transactionHash": transaction,
                                "blockTimestamp": req_body["event"]["data"]["block"][
                                    "timestamp"
                                ],
                            }
                        )
                    )
                    for transaction in transactions
                ]

                # Send all messages
                await sender.send_messages(messages)
                logging.info(
                    f"Sent {len(messages)} messages for transactions: {transactions}"
                )
    except KeyError as k:
        logging.critical(f"Error while creating the message: Key {k} doesn't exist.")
        return func.HttpResponse(status_code=500)
    except Exception as e:
        logging.critical(f"Unknown error while creating or sending the message: {e}")
        return func.HttpResponse(status_code=500)

    return func.HttpResponse(status_code=200)
