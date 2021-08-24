# System imports
import io
import subprocess

# External imports
from PIL import Image, ImageCms
from viaa.configuration import ConfigParser

# Internal imports
from .kakadu import Kakadu
from .helpers import get_file_name_without_extension, get_path_leaf

config = ConfigParser()


class FileTransformer:
    def __init__(self, configParser: ConfigParser = None):
        self.config: dict = configParser.app_cfg
        self.kakadu = Kakadu(self.config["kakadu"]["bin"])

    def crop_borders_and_color_charts(self, file_path) -> str:
        """Crop borders and color charts from image.

        Params:
            file_path: path to file

        Returns:
            Path to cropped image.
        """
        file_name = get_path_leaf(file_path)
        export_path = self.config["transform"]["path"]

        subprocess.call(
            "python colorchecker/detect.py"
            + f" --weights colorchecker/weights/best.pt --source \
                {file_path} --target {file_path} --crop \
                True --project {export_path} --name cropped --exist-ok",
            shell=True,
        )
        return f"{export_path}cropped/{file_name}"

    def resize(self, file_path, resize_params):
        """Resize image to given width and height.

        Params:
            file_path: path to file
            resize_params: (width, height): new dimensions
        """
        image = Image.open(file_path)
        resized_image = image.resize(resize_params)
        resized_image.save(file_path)

    def convert_to_srgb(self, file_path, icc):
        """Convert image to sRGB color space.

        Params:
            file_path: path to file
            icc: icc of the image
        """
        img = Image.open(file_path)

        if icc:
            # Create ICC color profiles
            file = io.BytesIO(icc)
            input_profile = ImageCms.ImageCmsProfile(file)
            output_profile = ImageCms.createProfile("sRGB")

            # Convert to output_profile
            # TODO: Disable conversion to 8bit
            img = ImageCms.profileToProfile(
                img,
                input_profile,
                output_profile,
                renderingIntent=ImageCms.INTENT_RELATIVE_COLORIMETRIC,
            )

            img.save(
                file_path,
                save_all=True,
                compression=None,
                quality=100,
                icc_profile=img.info.get("icc_profile"),
            )

        img.close()

    def encode_image(self, input_file_path) -> str:
        """Encode image to jp2 file using Kakadu.

        Params:
            input_file_path: path to file

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
            # "-jp2_space",
            # "sRGB",
        ]

        # Construct path to new image
        file_name = get_file_name_without_extension(input_file_path)
        output_file_path = self.config["transform"]["path"] + "/" + file_name + ".jp2"

        # Encode image using kdu_compress
        self.kakadu.kdu_compress(input_file_path, output_file_path, kakadu_options)

        return output_file_path
