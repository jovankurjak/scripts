#!/usr/bin/python3

# Used to parse input args
from sys import argv
import argparse
import os
import re

import options.unzip as zippin
import options.grepall as grepall
import options.cpu as cpu

# Program version
prog_version = '0.2'

# Importaint functions
systemApplications = [
    'medialauncher',
    'smartphone_integrator',
    'organizer',
    'connectivity_launcher',
    'navigation',
    'browser',
    'speech',
    'explorer',
    'esosearch',
    'sseProc',
    'EsoPosProvider',
    'radiodata',
    'esohwr',
    'audioProc',
    'GpsDriverProc',
    'persistence',
    'systemservices'
]


def get_args():
    """This function will be used to parse args

    Explanation of each option should be done here

    Args:

    Returns:

    Todo:
        * Add a workflow how to use parsed arguments
        * Define few options and how to use them
        * Define a default behaviour
        * Update help
    """
    parser = argparse.ArgumentParser(description='MIB2P analyze tool')
    parser.add_argument('dirname',
                        nargs='?',
                        help='Directory where operation/s should be performed')
    # parser.add_argument('-p',
    #                     '--pattern',
    #                     action="store",
    #                     type=str,
    #                     help='pattern that is used for search through file')
    parser.add_argument('-c',
                        '--cpu',
                        action='store_true',
                        default=False,
                        help='make a CPU analysis of an MMX file')
    parser.add_argument('-a',
                        '--all_keywords',
                        action='store_true',
                        default=False,
                        help='grep all keywords from available files. user can provide a directory')
    parser.add_argument('-z',
                        '--unzip',
                        action='store_true',
                        default=False,
                        help='extracting files recursevely (supported extensions: zip|7z|gz|tar)')
    parser.add_argument('-l',
                        '--list',
                        action='store_true',
                        default=False,
                        help='list all serial log files found in directory(recursevely)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(prog_version))

    # args = vars(parser.parse_args())
    args = parser.parse_args()

    # Print help if no arguments are provided
    if not len(argv) > 1:
        parser.print_help()

    return args


def get_mmx_serial_file_name(pattern):
    """Get file name of MMX serial log

    Returns:
        String: file name, None otherwise.

    """
    files_list = []
    # mmx, a15, m4, subcpu
    keywords = ['HB:', '\[CAR_CON\]', '\[BAP\]|\[M4PW\]|\[MAWD\]', '\d+\s+T:\d,\d|[\d]+[\s]+MMX Stop res$']

    files = [f for f in os.listdir('.') if os.path.isfile(f)]

    for i, key in enumerate(keywords):
        for f in files:
            if f.endswith(".txt"):
                if search_for_pattern(f, key):
                    # files_list[i] = f.__str__()
                    files_list.append(f.__str__())

    return files_list


def get_all_log_files(directory):
    """

    Returns:
        file_paths(dict): dictionary containing file names and keys for each file
    """
    # initializing empty file paths dictionary
    file_paths = {}
    # mmx, a15, m4, subcpu
    keywords = {'MMX': 'HB:',
                'A15': '\[CAR_MAS\]',
                'M4': '\[BAP\]|\[M4PW\]|\[MAWD\]',
                'SubCpu': '\d+\s+T:\d,\d|[\d]+[\s]+MMX Stop res$'}

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            if filename.endswith(".txt"):
                for key in keywords:
                    if search_for_pattern(filepath, keywords[key]):
                        file_paths[key] = filepath
    return file_paths


# searches for a certain pattern inside the log file
def search_for_pattern(f, pattern):
    result = False
    with open(f, 'r', encoding='utf8', errors='ignore') as book:
        # with open(f, 'r') as book:
        for line in book:
            line = line.rstrip()
            if re.search(pattern, line):
                result = True
                break
    return result


def main():
    args = get_args()
    # print(args)
    dir_name = args.dirname

    # get correct dir name. If dirname is not a directory or not provided, use current('.')
    if dir_name:
        if not os.path.isdir(dir_name):
            print('Dirname is not a directory!')
            dir_name = '.'
        else:
            print('Dirname is: {}'.format(dir_name))
    else:
        dir_name = '.'
        print('Dirname not provided')
    log_file_list = get_all_log_files(dir_name)

    if args.cpu:
        print('Option for CPU is active!')
        if 'MMX' not in log_file_list:
            print('No log files')
            return
        print('MMX file analyzed: {}'.format(log_file_list['MMX']))
        cpu.find_header(log_file_list['MMX'])

    if args.all_keywords:
        print('Option for all_keywords is active!')
        if bool(log_file_list):
            grepall.parse_all_files(log_file_list)

    if args.unzip:
        print('Unzip option is active!')
        zippin.find_files(dir_name)

    if args.list:
        print('List option is active!')

        if bool(log_file_list):
            for key in log_file_list.keys():
                print('file:[{0}] ({1})'.format(log_file_list[key], key))
        else:
            print('No files found!')


if __name__ == '__main__':
    main()
