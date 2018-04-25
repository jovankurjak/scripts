#!/usr/bin/python3

import os
import io
import re
import subprocess


def findFiles(directory):
    """Extract all files recursevely
    """
    for root, dirs, files in os.walk(str(directory)):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            if re.search(r".zip|.7z", filename):
                # dirname = filepath.split(".")[0]
                dirname = filepath
                # trim dir name for extensions
                dirname = re.sub(r"\.zip|\.7z\.\d+$", '', dirname)
                extract7z(filepath, dirname)
                findFiles(dirname)
    print("All folders are uncompressed!")


def extract7z(filename, dir):
    print('Extracting: filename:{0} dir={1}'.format(
        str(filename), str(dir)
    ))
    subprocess.call(r'"C:\Program Files\7-Zip\7z.exe" x ' + filename + ' -o' + dir)
