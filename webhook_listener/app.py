from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from config import Config
from aio_pika import Message, connect
import logging
import hmac
import hashlib
import json


# Alchemy signing key to validate the signature
SIGNING_KEY = Config.get_signing_key()


# Application initialization
app = FastAPI()


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


@app.post("/webhook")
async def process_webhook(req: Request):
    source_ip = req.headers.get("x-forwarded-for")
    # Verifies if the request is coming from an authorized IP address
    authorized_ips = Config.get_authorized_ips()
    if source_ip not in authorized_ips and len(authorized_ips) != 0:
        logging.error(f"Request coming from unauthorized IP address: {source_ip}")
        return JSONResponse(
            content={"status": "error", "message": "Unauthorized IP address"},
            status_code=403,
        )

    signature = req.headers.get("x-alchemy-signature")
    # Verify if the Alchemy signature is in the header
    if not signature:
        logging.error("Missing signature in headers.")
        return JSONResponse(
            content={"status": "error", "message": "Missing signature in headers"},
            status_code=400,
        )

    # Get the body content
    try:
        req_body_json = await req.json()
        req_body_raw = await req.body()
        logging.info(f"Body Size: {len(bytes(str(req_body_json), 'utf-8'))} bytes")
    except ValueError:
        logging.error("Missing body.")
        return JSONResponse(
            content={"status": "error", "message": "Missing body"}, status_code=400
        )
    except Exception as e:
        logging.error(f"Unknown error with the request body: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "message": "Unknown error with the request body",
            },
            status_code=400,
        )

    # Verify if the signature is valid
    if not is_valid_signature_for_string_body(req_body_raw, signature, SIGNING_KEY):
        logging.error("The signature is invalid.")
        return JSONResponse(
            content={"status": "error", "message": "Invalid signature"}, status_code=401
        )

    # Verify is there is a body to the request
    if not req_body_json:
        logging.error("Missing body.")
        return JSONResponse(
            content={"status": "error", "message": "Missing body"}, status_code=400
        )

    # Loop through received transactions and send a message to RabbitMQ for every transaction
    try:
        logs = req_body_json["event"]["data"]["block"]["logs"]
        # Create a list of unique transaction hash
        transactions = set([log["transaction"]["hash"] for log in logs])
        connection = await connect(Config.get_rabbitmq_connection_string())
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(
                Config.get_rabbitmq_queue_name(), durable=True
            )

            for transaction in transactions:
                # Create a message for each transaction
                message_body = {
                    "blockNumber": req_body_json["event"]["data"]["block"]["number"],
                    "transactionHash": transaction,
                    "blockTimestamp": req_body_json["event"]["data"]["block"][
                        "timestamp"
                    ],
                }

                # Send the message to RabbitMQ
                await channel.default_exchange.publish(
                    Message(json.dumps(message_body).encode("utf-8")),
                    routing_key=queue.name,
                )

                logging.info(f"Sent message for transaction: {transaction}")
    except KeyError as k:
        logging.critical(f"Error while creating the message: Key {k} doesn't exist.")
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Key {k} doesn't exist in the request body",
            },
            status_code=500,
        )
    except Exception as e:
        logging.critical(f"Unknown error while creating or sending the message: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "message": "Unknown error while creating or sending the message",
            },
            status_code=500,
        )

    return JSONResponse(
        content={"status": "success", "message": "Messages sent successfully"},
        status_code=200,
    )
