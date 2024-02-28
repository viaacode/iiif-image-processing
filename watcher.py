#!/usr/bin/env python

# System imports
import subprocess
import zipfile
from pathlib import Path
from os import walk, environ

# Internal imports
from app.helpers import get_iiif_file_destination, check_pronom_id
from viaa.observability import logging
from viaa.configuration import ConfigParser

# External imports
import inotify.adapters


"""
Listen to file write events in a directory.
If a relevant file is written in the directory, execute corresponding scripts.
Remove the original file after the scripts have been executed.
"""

if __name__ == '__main__':
    i = inotify.adapters.InotifyTree('/export/home')
    config = ConfigParser()
    logger = logging.get_logger('watcher', config)

    workfolder_base = '/opt/image-processing-workfolder'

    logger.info('Watching dir : %s', '/export/home')
    logger.debug('debug info')

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        # Only listen to write events
        if 'IN_CLOSE_WRITE' not in type_names:
            continue

        # Only look at zip files
        if not filename.endswith('.zip'):
            print(f'Ignoring file {filename}')
            continue

        # Unpack zip to working directory
        full_file_path = path + '/' + filename
        workfolder = workfolder_base + '/' + Path(full_file_path).stem

        logger.debug('got event for %s', full_file_path)

        try:
            with zipfile.ZipFile(full_file_path, 'r') as zip_ref:
                zip_ref.extractall(workfolder)
        except zipfile.BadZipFile:
            logger.debug('Invalid zip file %s', full_file_path)
            continue

        essence_files_in_workfolder = [
                file for file in next(walk(workfolder), (None, None, []))[2]
                if check_pronom_id(workfolder + '/' + file, 'fmt/353')  # Tagged Image File Format (tif)
                ]
        file_to_transform = essence_files_in_workfolder[0]

        metadata_files_in_workfolder = [
                file for file in next(walk(workfolder), (None, None, []))[2]
                if check_pronom_id(workfolder + '/' + file, 'fmt/101')  # Extensible Markup Language (xml)
                ]
        file_to_transform_path = workfolder + '/' + file_to_transform
        sidecar_path = workfolder + '/' + metadata_files_in_workfolder[0]

        destination = get_iiif_file_destination(file_to_transform_path, sidecar_path)

        my_env = environ.copy()
        my_env["PATH"] = f"/opt/iiif-image-processing/env/bin:{my_env['PATH']}"
        logger.debug('Running transform_file for %s', file_to_transform_path)
        logger.debug('Destination %s', destination)
        # Transform image by executing scripts
        subprocess.run(
            "python3 /opt/iiif-image-processing/transform_file.py"
            + f" --file_path {file_to_transform_path}"
            + f" --destination {destination}",
            shell=True,
            check=True,
            env=my_env
        )

        logger.debug('removing zip file %s', full_file_path)

        # Delete zip
        Path(full_file_path).unlink(missing_ok=True)
