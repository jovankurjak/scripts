#!/usr/bin/python3

import os
import io
import re
import subprocess


def findFiles(directory):
    """Extract all files recursevely
    """
    pattern = r"\.zip$|\.7z\.\d+$|\.7z$|\.gz$"  #r"\.zip|\.7z|\.gz$"
    for root, dirs, files in os.walk(str(directory)):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            if re.search(pattern, filename):
                dirname = filepath
                # trim dir name for extensions
                dirname = re.sub(pattern, '', dirname)
                print('dirname=[{0}]'.format(str(dirname)))
                extract7z(filepath, dirname)
                findFiles(dirname)
    print("All folders are uncompressed!")


def extract7z(filename, directory):
    """ Extracts filename into directory

    For .tar.gz files different command is used.
    command to use if tar.gz: 7z x "somename.tar.gz" -so | 7z x -aoa -si -ttar -o"somename"
        x     = Extract with full paths command
        -so   = write to stdout switch
        -si   = read from stdin switch
        -aoa  = Overwrite all existing files without prompt.
        -ttar = Treat the stdin byte stream as a TAR file
        -o    = output directory

    Args:
        filename: full path to file to extract
        directory: full path to directory to extract contents from filename

    Returns: empty

    """
    if re.search(r"\.tar\.gz$", filename):

        print('Extracting: filename:{0} dir={1}'.format(
            str(filename), str(re.sub(r"\.tar\.gz$", '', filename))
        ))
        command = "{0} x {1} -so | {0} x {1} -so | {0} x -aoa -si -ttar -o{2}".format(
            r'"C:\Program Files\7-Zip\7z.exe"',
            filename,
            re.sub(r"\.tar\.gz$", '', filename)
        )
        ps = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        # print(output)
    else:
        print('Extracting: filename:{0} dir={1}'.format(
            str(filename), str(directory)
        ))
        command = "{0} x {1} -o{2}".format(
            r'"C:\Program Files\7-Zip\7z.exe"',
            filename,
            directory
        )
        subprocess.call(command)