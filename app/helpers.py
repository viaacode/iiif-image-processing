# System imports
import ntpath
import os


def cmd_is_executable(cmd):
    """Check if command executable.

    Params:
        cmd: filepath to an executable.

    Returns:
        True if the command exists (including if it is on the PATH) and can be
        executed
    """
    if os.path.isabs(cmd):
        paths = [""]
    else:
        paths = [""] + os.environ["PATH"].split(os.pathsep)
    cmd_paths = [os.path.join(path, cmd) for path in paths]
    return any(
        os.path.isfile(cmd_path) and os.access(cmd_path, os.X_OK)
        for cmd_path in cmd_paths
    )


def get_path_leaf(path) -> str:
    """Get leaf of given path.

    Returns:
        leaf: string
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_file_name_without_extension(file_path) -> str:
    """Get name of file without its extension.

    Returns:
        name: string
    """
    file_name = get_path_leaf(file_path)
    return os.path.splitext(file_name)[0]
