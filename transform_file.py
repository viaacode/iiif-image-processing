# System imports
import argparse

# External imports
from viaa.configuration import ConfigParser

# Internal imports
from app.file_transformation import FileTransformer

"""
Script to apply transformations (crop, resize, convert color space and encode)
to an image file.
"""

if __name__ == "__main__":
    # Init
    configParser = ConfigParser()
    parser = argparse.ArgumentParser()

    # Get arguments
    parser.add_argument(
        "--file_name", type=str, default=None, help="Path to file", required=True
    )
    args = parser.parse_args()
    file_name = args.file_name

    # Transform file
    file_transformer = FileTransformer(configParser)

    # Get icc from image here, because it will be lost after
    # the 'crop_borders_and_color_charts' function has been executed
    # icc is needed to convert the color space to sRGB
    icc = file_transformer.get_icc(file_name)

    cropped_file = file_transformer.crop_borders_and_color_charts(file_name)
    # resize_params = file_transformer.calculate_resize_params(cropped_file)
    # file_transformer.resize(cropped_file, resize_params)
    file_transformer.convert_to_srgb(cropped_file, icc)
    encoded_file = file_transformer.encode_image(cropped_file)
