# System imports
import functools
import logging
import logging

# Internal imports
from viaa.configuration import ConfigParser
from helpers import remove_file
from mediahaven import MediaHaven
from mediahaven.resources.base_resource import MediaHavenPageObject
from mediahaven.mediahaven import MediaHavenException
from mediahaven.oauth2 import ROPCGrant

# External imports
import pika

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

config_parser = ConfigParser()

client_id = config_parser.app_cfg["mediahaven"]["client"]
client_secret = config_parser.app_cfg["mediahaven"]["secret"]
user = config_parser.app_cfg["mediahaven"]["username"]
password = config_parser.app_cfg["mediahaven"]["password"]
url = config_parser.app_cfg["mediahaven"]["host"]
grant = ROPCGrant(url, client_id, client_secret)
grant.request_token(user, password)
mediahaven_client = MediaHaven(url, grant)


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
        visibility = 'public' if 'public' in msg['path'] else 'restricted'
        fragment_id = msg["fragment_id"]
        
        export_dict = {
            "Records": [{
                "RecordId": fragment_id
            }],
            "ExportLocationId": config_parser.app_cfg["mediahaven"]["export_location_id"],
            "Reason": "IIIF image processing.",
            "Combine": "Zip",
            "DestinationPath": visibility
        }
        
        mediahaven_client._post("exports", json=export_dict)
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
