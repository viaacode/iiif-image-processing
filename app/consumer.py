# System imports
import functools
import logging
import logging

# Internal imports
from viaa.configuration import ConfigParser
from helpers import remove_file

# External imports
import pika

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def on_message(chan, method_frame, header_frame, body, userdata=None):
    """Called when a message is received. Log message and ack it."""
    LOGGER.info(
        "Delivery properties: %s, message metadata: %s", method_frame, header_frame
    )
    LOGGER.info("Userdata: %s, message body: %s", userdata, body)
    # Start image processing workflow

    # Convert string to object
    msg = eval(body.decode())
    method = msg["action"]

    if method == "create":
        # TODO: start export from MH
        fragment_id = msg["fragment_id"]
        print(f'TODO: start export from MH for fragment id {fragment_id}')
    elif method == "delete":
        visibility = 'public' if 'public' in msg['path'] else 'restricted'
        or_id = msg['OR-id']
        fragment_id = msg["fragment_id"]
        characters = fragment_id[:2]
        file_to_delete = '/export/images/'
        + visibility
        + "/"
        + or_id
        + "/"
        + characters
        + "/"
        + fragment_id
        + ".jph"
        print(f"deleting {file_to_delete}")
        remove_file(file_to_delete)

    print(f'fragment_id: {msg["fragment_id"]}')
    chan.basic_ack(delivery_tag=method_frame.delivery_tag)


def main():
    """Main method."""
    config_parser = ConfigParser()
    rabbit_config = config_parser.app_cfg["rabbitmq"]
    credentials = pika.PlainCredentials(
        rabbit_config["username"], rabbit_config["password"]
    )
    parameters = pika.ConnectionParameters(
        rabbit_config["host"], credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    on_message_callback = functools.partial(on_message, userdata="on_message_userdata")
    channel.basic_consume(rabbit_config["queue"], on_message_callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()


if __name__ == "__main__":
    main()
