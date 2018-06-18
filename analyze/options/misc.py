#!/usr/bin/python3
""" Miscellaneous functions that are used at top level.
Like writing to a file.
Function for drawing a graph needs 2 dependencies to
be installed => bokeh and pandas modules.

"""

import re

from bokeh.plotting import figure, output_file, show
import pandas as pd


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


def draw_cpu_graph(cpu_table, header_dict):
    """Draw a cpu graph from cpu_table

    Args:
        cpu_table:
        header_dict:

    Returns:

    """
    # Create a header for table
    header = []
    for key in header_dict:
        header.append(key)
    # print('header: ' + str(header))

    # Prepare a list for plotting
    cpu_list = []
    for dict_element in cpu_table:
        # 0 element of header is always 'time' and
        # 1st element of header is always 'CPU'
        if header[1] in dict_element:
            cpu_list.append(dict_element[header[1]])

    time_list = []
    for element in cpu_table:
        if header[0] in element:
            time_list.append(element[header[0]])

    # print('time: ' + str(time_list))

    # prepare some data
    df = pd.DataFrame(cpu_table)
    df['time'] = pd.to_datetime(df['time'])

    # output to static HTML file
    output_file("cpu_basic.html")

    # # create a new plot with a title and axis labels
    p = figure(title="simple line example",
               x_axis_label='time',
               x_axis_type='datetime',
               y_axis_label='cpu[%]',
               plot_width=1200,
               plot_height=400)

    p.line(df['time'], df['CPU'], color='navy', alpha=0.5)

    # show the results
    show(p)
