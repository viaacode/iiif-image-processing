# Internal imports
from app.helpers import (
    get_file_extension,
    get_file_name_without_extension,
    get_path_leaf,
    get_resize_params,
)


def test_get_file_extension_tiff():
    file_name = "filename.tiff"
    file_extension = get_file_extension(file_name)
    assert file_extension == ".tiff"


def test_get_file_extension_png():
    file_name = "filename.png"
    file_extension = get_file_extension(file_name)
    assert file_extension == ".png"


def test_get_file_extension_png_nested():
    file_name = "/long/path/to/filename.png"
    file_extension = get_file_extension(file_name)
    assert file_extension == ".png"


def test_get_file_extension_png_nested_relative():
    file_name = "long/path/to/filename.png"
    file_extension = get_file_extension(file_name)
    assert file_extension == ".png"


def test_get_file_name_without_extension():
    file_name = "filename.tiff"
    file_extension = get_file_name_without_extension(file_name)
    assert file_extension == "filename"


def test_get_file_name_without_extension_nested():
    file_name = "/long/path/to/filename.tiff"
    file_extension = get_file_name_without_extension(file_name)
    assert file_extension == "filename"


def test_get_file_name_without_extension_nested_relative():
    file_name = "long/path/to/filename.tiff"
    file_extension = get_file_name_without_extension(file_name)
    assert file_extension == "filename"


def test_get_path_leaf():
    file_name = "/long/path/to/filename.tiff"
    file_extension = get_path_leaf(file_name)
    assert file_extension == "filename.tiff"


def test_calculate_resize_params_sub_5000():
    width, height = get_resize_params(100, 50)
    assert width == 100
    assert height == 50


def test_calculate_resize_params_between_5000_and_15000():
    width, height = get_resize_params(7200, 12000)
    assert width == 6100
    assert height == 10167

    width, height = get_resize_params(14000, 9300)
    assert width == 9500
    assert height == 6311


def test_calculate_resize_params_plus_15000():
    width, height = get_resize_params(20000, 10000)
    assert width == 10000
    assert height == 5000
