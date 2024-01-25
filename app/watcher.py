# System imports
import subprocess
import zipfile
from pathlib import Path
from os import walk

# Internal imports
from helpers import get_iiif_file_destination

# External imports
import inotify.adapters


"""
Listen to file write events in a directory.
If a relevant file is written in the directory, execute corresponding scripts.
Remove the original file after the scripts have been executed.
"""

if __name__ == '__main__':
    i = inotify.adapters.InotifyTree('/tmp/subdir')

    folders_to_ignore = [
        '/export/home/public',
        '/export/home/restricted',
    ]

    workfolder_base = '/tmp/workdir'

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
        workfolder = workfolder_base + '/' + Path(full_file_path).stem
        try:
            with zipfile.ZipFile(full_file_path, 'r') as zip_ref:
                zip_ref.extractall(workfolder)
        except zipfile.BadZipFile:
            print(f'Invalid zip file {full_file_path}')

        essence_files_in_workfolder = [
                file for file in next(walk(workfolder), (None, None, []))[2]
                if file.endswith('.tif') or file.endswith('.tiff')
                ]
        file_to_transform = essence_files_in_workfolder[0]

        metadata_files_in_workfolder = [
                file for file in next(walk(workfolder), (None, None, []))[2]
                if file.endswith('.xml')
                ]
        file_to_transform_path = workfolder + '/' + file_to_transform
        sidecar_path = workfolder + '/' + metadata_files_in_workfolder[0]

        destination = get_iiif_file_destination(file_to_transform_path, sidecar_path)

        # Transform image by executing scripts
        subprocess.call(
            "python /opt/iiif-image-processing/transform_file.py"
            + f" --file_path {file_to_transform}"
            + f" --destination {destination}",
            shell=True,
        )

        # Delete zip
        Path(full_file_path).unlink(missing_ok=True)
