#!/usr/bin/python3

import collections
import re


def find_header(file):
    """Parse MMX serial log file

    This function goes through MMX log file and parses every
    HB section for overall CPU consumption and CPU consumption of
    currently active processes at that time
    """
    tell_position = 0
    header_counter = 0
    my_list = []
    my_dict = {}
    # csv_file = '/home/rtrk/Desktop/cpu.csv'
    csv_file = 'cpu_quick_analysis.csv'
    with open(file, 'r', encoding='utf8', errors='ignore') as fp:
        fp.seek(0, 2)
        e_o_f = fp.tell()
        fp.seek(0)

        print("Sum lines: " + len(fp.readlines()).__str__())
        while True:
            """parse the file"""
            # Check for e_o_f
            if tell_position == e_o_f:
                break
            cur_header_start = get_next_pattern(fp, tell_position, 'CPU=')
            tell_position = fp.tell()
            cur_header_end = get_next_pattern(fp, tell_position, 'System is')
            # Check for e_o_f
            if tell_position == e_o_f:
                break
            header_counter += 1
            tell_position_end = fp.tell()
            my_dict = dict.fromkeys(my_dict, '0')
            (my_list, my_dict) = parse_for_functions(fp, cur_header_start, cur_header_end, my_list, my_dict)
            tell_position = fp.tell()

        print('number of HB headers: ' + header_counter.__str__() + " end .tell() position:" + tell_position.__str__())

        with open(csv_file, "w") as output:
            """Write the list to csv file."""

            header = 'time,'
            all_values = ''
            for key in my_list[-1].keys():
                if key != 'time':
                    header += (key + ',')

            header += '\n'
            for values in my_list[-4].values():
                if my_list[-4]['time'] == values:
                    all_values = values + ',' + all_values
                else:
                    all_values += (values + ',')

            output.write(str(header))
            # print(header)
            # print(all_values)
            for entries in my_list:
                current_line = ''
                for key_up in my_list[-1].keys():
                    for key in entries.keys():
                        if key_up is key:
                            if key is 'time':
                                current_line = entries[key] + ',' + current_line
                            else:
                                current_line += (entries[key] + ',')
                            break
                    else:
                        current_line += ('0' + ',')

                # print(current_line)
                current_line += '\n'
                output.write(current_line)


def get_next_pattern(file_pointer, line_number, pattern):
    """Module function

    This function searches for 'pattern' starting from 'line_number'
    using file descriptor 'file_pointer'.
    """
    file_pointer.seek(line_number)
    current_tell = file_pointer.tell()
    for line_number, line in enumerate(iter(file_pointer.readline, '')):
        line = line.rstrip()
        # find first header
        # print(line)
        if re.search(pattern, line):
            break
        current_tell = file_pointer.tell()
    return current_tell


def parse_for_functions(file_pointer, start_position, end_position, my_list, my_dict):
    """Module function

    Args:
        file_pointer (file desc): file descriptor currently parsed object.
        start_position (int): from what position in file to start parsing.
        end_position (int): to what position in file to parse.
        my_list (List): List containing rows of the CPU table.
        my_dict (Dictionary): Dictionary containing values for 1 row of my_list.
    """
    file_pointer.seek(start_position + 1)
    for line_number, line in enumerate(iter(file_pointer.readline, '')):
        if file_pointer.tell() == end_position:
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
            re_obj = re.search(regex, line)
            if re_obj:
                # Add items to the list - start row
                my_dict['time'] = re_obj.group(1)
                my_dict['CPU'] = re_obj.group(2)
                # print('CPU={0}; time={1}'.format(
                #     re_obj.group(2).__str__(),
                #     re_obj.group(1).__str__()))
        else:
            # regex for function and percentage
            regex = r"\b(\d+:\d+:\d+)[.\d\s]+\|[\s\d:]+HB:\s+[\b\w+\/.]+\/([\w-]+)\s+\(\d+\)\s([\d.]+)%"
            re_obj = re.search(regex, line)
            if re_obj:
                my_dict[re_obj.group(2).__str__()] = re_obj.group(3)
                # # Add items to the list
                # print('{0}; {1} -> {2}%'.format(
                #     re_obj.group(1).__str__(),
                #     re_obj.group(2).__str__(),
                #     re_obj.group(3).__str__()))
    return my_list, my_dict
