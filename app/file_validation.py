# External imports
from jpylyzer import jpylyzer

# Internal imports
from .helpers import get_icc, get_metadata_from_image
from viaa.configuration import ConfigParser


class FileValidator:
    def __init__(self, file_path, configParser: ConfigParser = None):
        self.config: dict = configParser.app_cfg
        self.result = jpylyzer.checkOneFile(file_path)

    def validate_ppi(self, file_path, expected_ppi=300):
        print("validate_ppi: TODO")

    def validate_icc(self, file_path, expected_icc="sRGB"):
        icc = get_icc(file_path)
        print("validate_icc: TODO")

    def validate_metadata(self, file_path, expected_metadata_tags=""):
        metadata = get_metadata_from_image(file_path)
        print(f'validate_metadata: {self.result.findtext("./properties/uuidBox/uuid")}')

    def validate_file_format(self, file_path, expected_file_format="jp2"):
        print(f'validate_file_format: {self.result.findtext("./isValid")}')
        valid = self.result.findtext("./isValid")
        print(f"valid file format: {valid}")

    def validate_file_name(self, file_path, expected_file_name=""):
        print(f'validate_file_name: {self.result.findtext("./fileInfo/fileName")}')
        return self.result.findtext("./fileInfo/fileName")

        # print(f'validate_file_format: {result.findtext("./properties/jp2HeaderBox
        # /imageHeaderBox/height")}')

    def validate_file_path(self, file_path, expected_file_path=""):
        print(f"validate_file_path: {file_path}")


# The output file contains the following top-level elements
#     One toolInfo element, which contains information about jpylyzer (its name and
#       version number)
#     One or more file elements, each of which contain information about about the
#        analysed files
# In turn, each file element contains the following sub-elements:
#     fileInfo: general information about the analysed file
#     statusInfo: information about the status of jpylyzer's validation attempt
#     isValid: outcome of the validation
#     tests: outcome of the individual tests that are part of the validation process
#        (organised by box)
#     properties: image properties (organised by box)
#     propertiesExtension: wrapper element for NISO MIX output (only if the --mix
#        option is used)
