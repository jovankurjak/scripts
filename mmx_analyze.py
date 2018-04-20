#!/usr/bin/python3

# Used to parse input args
from sys import argv
import argparse
import os
import re
import csv
import collections

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
                        nargs='+',
                        help='pattern that is used for search through file')
    parser.add_argument('-c',
                        '--cpu',
                        action='store_true',
                        default=False,
                        help='make a CPU analysis of an MMX file in current folder')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(prog_version))

    # args = vars(parser.parse_args())
    args = parser.parse_args()
    print(args)
    print("print cpu={0}".format(args.cpu.__str__()))
    print("print pattern={0}".format(args.pattern.__str__()))

    return args


def getMmxSerialFileName():
    """Get file name of MMX serial log

    Returns:
        String: file name, None otherwise.

    """
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if f.endswith(".txt"):
            if searchForPattern(f, 'HB:'):
                return f.__str__()
    return None


# searches for a certain pattern inside the log file
def searchForPattern(f, pattern):
    result = False
    # with open(f, 'r', encoding='latin-1') as book:
    with open(f, 'r') as book:
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
    log_file_name = getMmxSerialFileName()
    if log_file_name is None:
        print('ERROR: file not found!')
        return
    print("Log file: " + log_file_name + "\n")
    if args.cpu is True:
        findHeader(log_file_name)
    else:
        print('No option selected! use -h for help')


if __name__ == '__main__':
    main()
