#!/usr/bin/python3

# Used to parse input args
from sys import argv
import argparse
import os
import re
import csv


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
    myLine = None
    with open(f) as book:
        lines = book.readlines()
        lastline = lines[-1]
        for line in lines:
            myLine = line
            line = line.rstrip()
            if re.search(pattern, line):
                break

        if myLine is lastline:
            return False
        else:
            return True

def index(filename, patterns):
    with open(filename) as fp:
        for line_number, line in enumerate(fp):
            line = line.rstrip()
            # Find first header
            # if re.search('CPU=', line):
            #     print(line_number.__str__() + " " + line)
            for pat in patterns:
                if re.search(pat, line):
                    print(line_number.__str__() + " " + line)


# find headers in provided file
def findHeader(file):
    curHeaderStart = 0
    curHeaderEnd = 0
    tellPosition = 0
    tellPositionEnd = 0
    headerCounter = 0
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
            parseForFunctions(fp, curHeaderStart, curHeaderEnd)
            tellPosition = fp.tell()

        print(headerCounter.__str__() + " " + tellPosition.__str__())


# novi patern regex = r"\/([\w-]+)\s+\(\d+\)\s([\d.]+)%|(CPU)=(\d+)%"
# patern za vreme time_regex = r"\b(\d+:\d+:\d+).\d\s+\|"


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



def parseForFunctions(filePointer, startPosition, endPosition):
    filePointer.seek(startPosition + 1)

    for line_number, line in enumerate(iter(filePointer.readline, '')):
        if filePointer.tell() == endPosition:
            break
        line = line.rstrip()
        # check if header
        if re.search('CPU=', line) is not None:
            regex = r"(\d\d:\d\d:\d\d)\.\d\s+\|[\s\w:]+T=\d+C,\s+CPU=(\d+)"
            reObj = re.search(regex, line)
            if reObj:
                print('CPU={0}; time={1}'.format(
                    reObj.group(2).__str__(),
                    reObj.group(1).__str__()))
        else:
            # regex for function and percentage
            # regex = r"\/([\w-]+)\s+\(\d+\)\s([\d.]+)%"
            regex = r"\b(\d+:\d+:\d+).\d\s+\|[\s\d:]+HB:\s+[\b\w+\/]+\/([\w-]+)\s+\(\d+\)\s([\d.]+)%"
            reObj = re.search(regex, line)
            if reObj:
                print('{0}; {1} -> {2}%'.format(
                    reObj.group(1).__str__(),
                    reObj.group(2).__str__(),
                    reObj.group(3).__str__()))



def main():
    # args = getArgs()
    log_file_name = getMmxSerialFileName()
    print("Log file: " + log_file_name + "\n")
    parseAll(log_file_name)
    findHeader(log_file_name)

    # index(logFileName, patterns=('dump', 'ErrorDump', 'trigger'))


if __name__ == '__main__':
    main()
