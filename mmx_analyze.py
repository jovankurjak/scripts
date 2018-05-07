#!/usr/bin/python3

# Used to parse input args
from sys import argv
import argparse
import os
import re
import csv
import collections

import helper
import unzip

# Program version
prog_version = '0.1'

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

def getArgs():
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
    parser.add_argument('-p',
                        '--pattern',
                        action="store",
                        type=str,
                        help='pattern that is used for search through file')
    parser.add_argument('-c',
                        '--cpu',
                        action='store_true',
                        default=False,
                        help='make a CPU analysis of an MMX file in current folder')
    parser.add_argument('-a',
                        '--all_keywords',
                        action='store_true',
                        default=False,
                        help='search through all the files for their respective keywords')
    parser.add_argument('-z',
                        '--unzip',
                        action='store_true',
                        default=False,
                        help='test for unziping recursevely either zip or 7z')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(prog_version))

    # args = vars(parser.parse_args())
    args = parser.parse_args()
    print(args)
    print("print cpu={0}".format(args.cpu.__str__()))
    print("print pattern={0}".format(args.pattern.__str__()))

    return args


def getMmxSerialFileName(pattern):
    """Get file name of MMX serial log

    Returns:
        String: file name, None otherwise.

    """
    files_list = []
    # mmx, a15, m4, subcpu
    keywords = ['HB:', '\[CAR_CON\]', '\[MAWD\]', '\d+\s+T:\d,\d']

    files = [f for f in os.listdir('.') if os.path.isfile(f)]

    for i, key in enumerate(keywords):
        for f in files:
            if f.endswith(".txt"):
                if searchForPattern(f, key):
                    # files_list[i] = f.__str__()
                    files_list.append( f.__str__())

    return files_list


def getAllLogFiles(directory):
    """

    Returns:
        file_paths(dict): dictionary containing file names and keys for each file
    """
    # initializing empty file paths dictionary
    file_paths = {}
    # mmx, a15, m4, subcpu
    keywords = {'MMX': 'HB:',
                'A15': '\[CAR_MAS\]',
                'M4': '\[MAWD\]',
                'SubCpu': '\d+\s+T:\d,\d'}

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            if filename.endswith(".txt"):
                for key in keywords:
                    if searchForPattern(filepath, keywords[key]):
                        file_paths[key] = filepath
    return file_paths


# searches for a certain pattern inside the log file
def searchForPattern(f, pattern):
    result = False
    with open(f, 'r', encoding='utf8', errors='ignore') as book:
    # with open(f, 'r') as book:
        for line in book:
            line = line.rstrip()
            if re.search(pattern, line):
                result = True
                break
    return result


# find headers in provided file
def findHeader(file):
    """Parse MMX serial log file

    This function goes through MMX log file and parses every
    HB section for overall CPU consumption and CPU consumption of
    currently active processes at that time
    """
    tellPosition = 0
    headerCounter = 0
    mylist = []
    my_dict = {}
    # csvfile = '/home/rtrk/Desktop/cpu.csv'
    csvfile = 'cpu_quick_analysis.csv'
    with open(file) as fp:
        fp.seek(0, 2)
        EOF = fp.tell()
        fp.seek(0)

        print("Sum lines: " + len(fp.readlines()).__str__())
        while(True):
            """parse the file"""
            # Check for EOF
            if tellPosition == EOF:
                break
            curHeaderStart = getNextPattern(fp, tellPosition, 'CPU=')
            tellPosition = fp.tell()
            curHeaderEnd = getNextPattern(fp, tellPosition, 'System is')
            # Check for EOF
            if tellPosition == EOF:
                break
            headerCounter += 1
            tellPositionEnd = fp.tell()
            my_dict = dict.fromkeys(my_dict, '0')
            (mylist, my_dict) = parseForFunctions(fp, curHeaderStart, curHeaderEnd, mylist, my_dict)
            tellPosition = fp.tell()

        print('number of HB headers: ' + headerCounter.__str__() + " end .tell() position:" + tellPosition.__str__())

        with open(csvfile, "w") as output:
            """Write the list to csv file."""

            header = 'time,'
            allvalues = ''
            for key in mylist[-1].keys():
                if key != 'time':
                    header += (key + ',')

            header += '\n'
            for values in mylist[-4].values():
                if mylist[-4]['time'] == values:
                    allvalues = values + ',' + allvalues
                else:
                    allvalues += (values + ',')

            output.write(str(header))
            # print(header)
            # print(allvalues)
            for entries in mylist:
                currentline = ''
                for key_up in mylist[-1].keys():
                    for key in entries.keys():
                        if key_up is key:
                            if key is 'time':
                                currentline = entries[key] + ',' + currentline
                            else:
                                currentline += (entries[key] + ',')
                            break
                    else:
                        currentline += ('0' + ',')

                # print(currentline)
                currentline += '\n'
                output.write(currentline)


def getNextPattern(filePointer, lineNumber, pattern):
    """Module function

    This function searches for 'pattern' starting from 'lineNumber'
    using file descriptor 'filePointer'.
    """
    filePointer.seek(lineNumber)
    current_tell = filePointer.tell()
    for line_number, line in enumerate(iter(filePointer.readline, '')):
        line = line.rstrip()
        # find first header
        # print(line)
        if re.search(pattern, line):
            break
        current_tell = filePointer.tell()
    return current_tell


def parseForFunctions(filePointer, startPosition, endPosition, my_list, my_dict):
    """Module function

    Args:
        filePointer (file desc): file descriptor currently parsed object.
        startPosition (int): from what position in file to start parsing.
        endPosition (int): to what position in file to parse.
        my_list (List): List containing rows of the CPU table.
        my_dict (Dictionary): Dictionary containing values for 1 row of my_list.
    """
    filePointer.seek(startPosition + 1)
    for line_number, line in enumerate(iter(filePointer.readline, '')):
        if filePointer.tell() == endPosition:
            # End list row
            od = collections.OrderedDict(sorted(my_dict.items()))
            my_list.append(od)
            # print(od)
            # print_od = ''
            # for key in od:
            #     print_od += '[' + key + ':' + od[key] + '%' + '] '
            # print(print_od)
            for value in my_dict.values():
                value = ''
            break
        line = line.rstrip()
        # check if header
        if re.search('CPU=', line) is not None:
            regex = r"(\d\d:\d\d:\d\d)[\s.\d]+\|[\s\w:]+T=\d+C,\s+CPU=(\d+)"
            reObj = re.search(regex, line)
            if reObj:
                # Add items to the list - start row
                my_dict['time'] = reObj.group(1)
                my_dict['CPU'] = reObj.group(2)
                # print('CPU={0}; time={1}'.format(
                #     reObj.group(2).__str__(),
                #     reObj.group(1).__str__()))
        else:
            # regex for function and percentage
            regex = r"\b(\d+:\d+:\d+)[.\d\s]+\|[\s\d:]+HB:\s+[\b\w+\/.]+\/([\w-]+)\s+\(\d+\)\s([\d.]+)%"
            reObj = re.search(regex, line)
            if reObj:
                my_dict[reObj.group(2).__str__()] = reObj.group(3)
                # # Add items to the list
                # print('{0}; {1} -> {2}%'.format(
                #     reObj.group(1).__str__(),
                #     reObj.group(2).__str__(),
                #     reObj.group(3).__str__()))
    return (my_list, my_dict)



def main():
    args = getArgs()
    log_file_list = getAllLogFiles('.')
    for key in log_file_list.keys():
        print('file:[{0}] ({1})'.format(log_file_list[key], key))

    #Apply arguments
    if args.cpu is True:
        if log_file_list is None:
            print('ERROR: file not found!')
            return
        findHeader(log_file_list['MMX'])
    elif args.pattern is not None:
        print(args.pattern)
        if args.pattern == '1':
            helper.parse_all_files(getAllLogFiles('.'))
        else:
            # TODO: make a separate option. this is temporary
            helper.parseMMX(args.pattern)
    elif args.all_keywords is True:
        print('all_keywords is true')
        unzip.findFiles('.')
        log_files = getAllLogFiles('.')
        for key in log_files.keys():
            print('file:[{0}] ({1})'.format(log_files[key], key))
        helper.parse_all_files(getAllLogFiles('.'))
    elif args.unzip is True:
        print('unzip is true')
        unzip.extractAll('.')
    else:
        print('No option selected! use -h for help')


if __name__ == '__main__':
    main()
