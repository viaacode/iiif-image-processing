# System imports
import subprocess
import zipfile
from pathlib import Path

# External imports
import inotify.adapters


"""
Listen to file write events in a directory.
If a relevant file is written in the directory, execute corresponding scripts.
Remove the original file after the scripts have been executed.
"""

if __name__ == '__main__':
    i = inotify.adapters.InotifyTree('/export/home')

    folders_to_ignore = [
        '/export/home/public',
        '/export/home/restricted',
    ]

    workfolder = '/opt/image-processing-workfolder'

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        if path in folders_to_ignore:
            # todo: logging
            continue

        # Only listen to write events
        if 'IN_CLOSE_WRITE' not in type_names:
            continue

        print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
              path, filename, type_names))

        # Only look at zip files
        if not filename.endswith('.zip'):
            print(f'Ignoring file {filename}')
            continue

        # Unpack zip to working directory
        full_file_path = path + '/' + filename
        try:
            with zipfile.ZipFile(full_file_path, 'r') as zip_ref:
                zip_ref.extractall(workfolder)
        except zipfile.BadZipFile:
            print(f'Invalid zip file {full_file_path}')

        # Transform image by executing scripts
        subprocess.call(
            "python /opt/iiif-image-processing/transform_file.py"
            + f" --file-path {workfolder}/{path}",
            shell=True,
        )

        # Delete zip
        Path(full_file_path).unlink(missing_ok=True)
