#!/usr/bin/python3
""" CPU module """

import re


def find_header(file):
    """Parse MMX serial log file

    This function goes through MMX log file and parses every
    HB section for overall CPU consumption and CPU consumption of
    currently active processes at that time
    """
    tell_position = 0
    list_of_cpu_stats = []    # list in which all cpu activity results are kept
    header_key_values = {}   # dictionary variable to store current row of cpu activity
    # csv_file = '/home/rtrk/Desktop/cpu.csv'
    csv_file = 'cpu_quick_analysis.csv'
    with open(file, 'r', encoding='utf8', errors='ignore') as file_pointer:
        file_pointer.seek(0, 2)
        e_o_f = file_pointer.tell()
        file_pointer.seek(0)

        print("Sum lines: " + len(file_pointer.readlines()).__str__())
        while True:
            # parse the file
            # Check for e_o_f
            if tell_position == e_o_f:
                break
            cur_header_start = get_next_pattern(file_pointer, tell_position, 'CPU=')
            tell_position = file_pointer.tell()
            cur_header_end = get_next_pattern(file_pointer, tell_position, 'System is')
            # Check for e_o_f
            if tell_position == e_o_f:
                break
            parse_for_functions(file_pointer,
                                cur_header_start,
                                cur_header_end,
                                list_of_cpu_stats,
                                header_key_values)
            tell_position = file_pointer.tell()

        print('number of HB headers: '
              + len(list_of_cpu_stats).__str__()
              + " end .tell() position:"
              + tell_position.__str__())

    return list_of_cpu_stats, header_key_values


def get_next_pattern(file_pointer, line_number, pattern):
    """Module function

    This function searches for 'pattern' starting from 'line_number'
    using file descriptor 'file_pointer'.
    """
    file_pointer.seek(line_number)
    current_tell = file_pointer.tell()
    for line in iter(file_pointer.readline, ''):
        line = line.rstrip()
        # find first header
        if re.search(pattern, line):
            break
        current_tell = file_pointer.tell()
    return current_tell


def parse_for_functions(file_pointer, start_position, end_position, list_of_headers, key_values):
    """Module function

    Args:
        file_pointer (file desc): file descriptor currently parsed object.
        start_position (int): from what position in file to start parsing.
        end_position (int): to what position in file to parse.
        list_of_headers (List): List containing rows of the CPU table.
        key_values (Dictionary): Set containing keywords for a row of my_list(cumulative).


    """
    file_pointer.seek(start_position + 1)
    header_dict = {}
    for line in iter(file_pointer.readline, ''):
        if file_pointer.tell() == end_position:
            # End list row
            # ordered_dictionary = collections.OrderedDict(header_dict)
            list_of_headers.append(header_dict)
            break
        line = line.rstrip()
        # check if header
        if re.search('CPU=', line) is not None:
            regex = r"(\d\d:\d\d:\d\d)[\s.\d]+\|[\s\w:]+T=\d+C,\s+CPU=(\d+)"
            re_obj = re.search(regex, line)
            if re_obj:
                # Add items to the list - start row
                header_dict['time'] = re_obj.group(1)
                header_dict['CPU'] = re_obj.group(2)
                # Add to header set
                key_values['time'] = 1
                key_values['CPU'] = 2

        else:
            # regex for function and percentage
            regex = r"\b(\d+:\d+:\d+)[.\d\s]+\|[\s\d:]+HB:" \
                    r"\s+[\b\w+\/.]+\/([\w-]+)\s+\(\d+\)\s([\d.]+)%"
            re_obj = re.search(regex, line)
            if re_obj:
                header_dict[re_obj.group(2).__str__()] = re_obj.group(3)
                key_values[re_obj.group(2).__str__()] = 3
