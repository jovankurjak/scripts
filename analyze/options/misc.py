#!/usr/bin/python3
""" Miscellaneous functions that are used at top level.
Like writing to a file.

"""

import re


def write_to_csv(cpu_table, header_dict, csv_file):
    """Write cpu table to csv file

    Args:
        cpu_table:      table of all cpu activity in a MMX file
                        in a form of list of dictionaries
        header_dict:    keys represent header of the file
        csv_file:       name of the file to write the output

    Returns:

    """
    regex = r"\.csv$"
    write_file = csv_file
    if not re.search(regex, csv_file):
        write_file += '.csv'

    with open(write_file, "w") as output:
        # Write the list to csv file.

        # Create a header for table
        header = ''
        for key in header_dict:
            header += (key + ',')
        header += '\n'
        # Write header as first line in file
        print('HEADER: ' + header)
        output.write(header)

        for entries in cpu_table:
            current_line = ''
            # Align entry key values with header key values,
            # filling blank key values with zeroes
            for header_key in header_dict:
                if header_key in entries:
                    current_line += (entries[header_key] + ',')
                else:
                    current_line += ('0' + ',')
            current_line += '\n'
            output.write(current_line)
