# System imports
import io
import subprocess

# External imports
from PIL import Image, ImageCms
from PIL.ImageCms import applyTransform

# Internal imports
from .kakadu import Kakadu
from .helpers import get_file_name_without_extension, get_path_leaf
from viaa.configuration import ConfigParser

config = ConfigParser()


class FileTransformer:
    def __init__(self, configParser: ConfigParser = None):
        self.config: dict = configParser.app_cfg
        self.kakadu = Kakadu(self.config["kakadu"]["bin"])

    def get_icc(self, file_name):
        """Get icc_profile from image.

        Returns:
            icc
        """
        img = Image.open(file_name)
        icc = img.info.get("icc_profile")
        img.close()
        return icc

    def crop_borders_and_color_charts(self, file_path) -> str:
        """Crop borders and color charts from image.

        Returns:
            Path to cropped image.
        """
        file_name = get_path_leaf(file_path)
        export_path = self.config["transform"]["path"]
        subprocess.call(
            "python colorchecker/detect.py"
            + f" --weights colorchecker/weights/best.pt --source {file_path} --crop \
                True --project {export_path} --name cropped --exist-ok",
            shell=True,
        )
        return f"{export_path}cropped/{file_name}"

    def calculate_resize_params(self, file_name):
        print(f"TODO: calculate resize_params for {file_name}")

    def resize(self, file_name, resize_params):
        print(f"TODO: resize {file_name}")

    def convert_to_srgb(self, file_name, icc):
        """Convert image to sRGB color space (if possible)."""
        img = Image.open(file_name)

        if icc:
            # Create ICC color profiles
            file = io.BytesIO(icc)
            input_profile = ImageCms.ImageCmsProfile(file)
            output_profile = ImageCms.createProfile("sRGB")

            # Build and apply transformation
            transformation = ImageCms.buildTransform(
                input_profile, output_profile, img.mode, "RGB"
            )
            applyTransform(img, transformation, inPlace=True)

        img.close()

    def encode_image(self, input_file_path) -> str:
        """Encode image to jp2 file using Kakadu.

        Returns:
            Path to encoded image
        """
        kakadu_options = [
            "Clevels=6",
            "Clayers=6",
            "Cprecincts={256,256},{256,256},{128,128}",
            "Stiles={512,512}",
            "Corder=RPCL",
            "ORGgen_plt=yes",
            "ORGtparts=R",
            "Cblk={64,64}",
            "Cuse_sop=yes",
            "Cuse_eph=yes",
            "-flush_period",
            "1024",
            "-jp2_space",
            "sRGB",
        ]

        # Construct path to new image
        file_name = get_file_name_without_extension(input_file_path)
        output_file_path = self.config["transform"]["path"] + "/" + file_name + ".jp2"

        # Encode image using kdu_compress
        self.kakadu.kdu_compress(input_file_path, output_file_path, kakadu_options)

        return output_file_path
