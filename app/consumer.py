"""Basic message consumer example"""
# System imports
import functools
import logging

# Internal imports
from viaa.configuration import ConfigParser

# External imports
import pika
from pika.exchange_type import ExchangeType

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def on_message(chan, method_frame, header_frame, body, userdata=None):
    """Called when a message is received. Log message and ack it."""
    LOGGER.info('Delivery properties: %s, message metadata: %s', method_frame, header_frame)
    LOGGER.info('Userdata: %s, message body: %s', userdata, body)
    chan.basic_ack(delivery_tag=method_frame.delivery_tag)


def main():
    """Main method."""
    config_parser = ConfigParser()
    rabbit_config = config_parser.app_cfg['rabbitmq']
    credentials = pika.PlainCredentials(rabbit_config['rabbitmq']['username'], rabbit_config['password'])
    parameters = pika.ConnectionParameters(rabbit_config['host'], credentials=credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    on_message_callback = functools.partial(
        on_message, userdata='on_message_userdata')
    channel.basic_consume('iiif-image-processing-q', on_message_callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()


if __name__ == '__main__':
    main()
