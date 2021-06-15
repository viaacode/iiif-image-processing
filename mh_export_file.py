# System imports
import argparse

# Internal imports
from app.mediahaven import MediahavenClient
from viaa.configuration import ConfigParser

"""
Script to trigger an export from MediaHaven.
"""

if __name__ == "__main__":
    # Init
    configParser = ConfigParser()
    mh_client = MediahavenClient(configParser)
    argument_parser = argparse.ArgumentParser()

    # Get arguments
    argument_parser.add_argument(
        "--pid",
        type=str,
        default=None,
        help="Pid of the essence to be exported",
        required=True,
    )
    args = argument_parser.parse_args()
    pid = args.pid

    # Get media_object_id for this pid
    media_object_id = mh_client.get_media_object_id(pid)

    # Create export job
    essence_json = mh_client.export_essence(media_object_id)
