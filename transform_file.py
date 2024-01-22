# System imports
import argparse

# External imports
from viaa.configuration import ConfigParser

# Internal imports
from app.file_transformation import FileTransformer

# from app.file_validation import FileValidator
from app.helpers import (
    copy_file,
    copy_metadata,
    get_metadata_from_image,
    get_resize_params,
    get_file_extension,
    get_icc,
    get_image_dimensions,
    remove_file,
    rename_file,
)

"""
Script to apply transformations (crop, resize, convert color space, encode,
add metadata) to an image file.
"""

if __name__ == "__main__":
    # Init
    configParser = ConfigParser()
    parser = argparse.ArgumentParser()
    file_transformer = FileTransformer(configParser)

    # Get arguments
    parser.add_argument(
        "--file_path", type=str, default=None, help="Path to file", required=True
    )
    args = parser.parse_args()
    file_path = args.file_path

    # Copy file and rename it to external_id.
    # File has to be copied so metadata can be added again later.
    extension = get_file_extension(file_path)
    external_id = 'todo'
    copied_file_path = copy_file(file_path)
    file_path = rename_file(file_path, external_id + extension)

    # Get metadata from original image
    metadata = get_metadata_from_image(file_path)

    # Get icc from image here, because it will be lost after
    # the 'crop_borders_and_color_charts' function has been executed.
    # The original icc is needed to convert the color space to sRGB.
    icc = get_icc(file_path)

    # Crop file
    cropped_file = file_path

    # Resize file
    width, height = get_image_dimensions(cropped_file)
    max_dimensions = None
    resize_params = get_resize_params(width, height, max_dimensions)
    file_transformer.resize(cropped_file, resize_params)

    # Change color space
    file_transformer.convert_to_srgb(cropped_file, icc)

    # Encode to jp2
    encoded_file = file_transformer.encode_image(cropped_file)

    # Add metadata to file
    copy_metadata(copied_file_path, encoded_file)

    # Cleanup
    remove_file(copied_file_path)
