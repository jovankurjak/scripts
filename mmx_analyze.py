#!/usr/bin/python3

# Used to parse input args
from sys import argv
import argparse
import os
import re
import csv
import collections


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

mydict = {}
mylist = []


# Use to get arguments if needed
def getArgs():
    parser = argparse.ArgumentParser(description='Search log for keywords')
    parser.add_argument('pattern', action="store", type=str, nargs='+',
                   help='pattern that is used for search through file')
    parser.add_argument('-c'
                        , nargs='?', help='show only the count of the provided pattern through file')

    args = parser.parse_args()
    print(args)
    # print ("Starting script %s" % (argv[0]))
    #
    # print ("Number of arguments: ", len(argv))
    # print ("The arguments are: ", str(argv))


# Search for log that contains MMX data(pattern 'HB:')
# and return log file name
def getMmxSerialFileName():
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if f.endswith(".txt"):
            if searchForPattern(f, 'HB:'):
                return f.__str__()


def parseAll(file):
    with open(file) as fp:
        print("Sum lines: " + len(fp.readlines()).__str__())


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
    """
    This function goes through MMX log file and parses every
    HB section for overall CPU consumption and CPU consumption of
    currently active processes at that time
    """
    tellPosition = 0
    headerCounter = 0
    csv_list = []
    # csvfile = '/home/rtrk/Desktop/cpu.csv'
    csvfile = 'cpu_quick_analysis.csv'
    with open(file) as fp:
        fp.seek(0, 2)
        EOF = fp.tell()
        print(EOF)
        fp.seek(0)

        while(True):
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
            parseForFunctions(fp, curHeaderStart, curHeaderEnd, csv_list)
            tellPosition = fp.tell()

        print('number of HB headers: ' + headerCounter.__str__() + " " + tellPosition.__str__())

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


def parseForFunctions(filePointer, startPosition, endPosition, csv_list):
    filePointer.seek(startPosition + 1)
    for line_number, line in enumerate(iter(filePointer.readline, '')):
        if filePointer.tell() == endPosition:
            # End list row
            csv_list.append('\n')
            od = collections.OrderedDict(sorted(mydict.items()))
            mylist.append(od)
            # print(od)
            # print_od = ''
            # for key in od:
            #     print_od += '[' + key + ':' + od[key] + '%' + '] '
            # print(print_od)
            for value in mydict.values():
                value = ''
            break
        line = line.rstrip()
        # check if header
        if re.search('CPU=', line) is not None:
            regex = r"(\d\d:\d\d:\d\d)[\s.\d]+\|[\s\w:]+T=\d+C,\s+CPU=(\d+)"
            reObj = re.search(regex, line)
            if reObj:
                # Add items to the list - start row
                csv_list.extend([reObj.group(1),  ',', reObj.group(2)])
                mydict['time'] = reObj.group(1)
                mydict['CPU'] = reObj.group(2)
                # print('CPU={0}; time={1}'.format(
                #     reObj.group(2).__str__(),
                #     reObj.group(1).__str__()))
        else:
            # regex for function and percentage
            regex = r"\b(\d+:\d+:\d+)[.\d\s]+\|[\s\d:]+HB:\s+[\b\w+\/.]+\/([\w-]+)\s+\(\d+\)\s([\d.]+)%"
            reObj = re.search(regex, line)
            if reObj:
                mydict[reObj.group(2).__str__()] = reObj.group(3)
                # # Add items to the list
                # print('{0}; {1} -> {2}%'.format(
                #     reObj.group(1).__str__(),
                #     reObj.group(2).__str__(),
                #     reObj.group(3).__str__()))



def main():
    # args = getArgs()
    log_file_name = getMmxSerialFileName()
    print("Log file: " + log_file_name + "\n")
    parseAll(log_file_name)
    findHeader(log_file_name)


if __name__ == '__main__':
    main()
