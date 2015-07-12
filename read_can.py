#! /usr/bin/env python
#
# Run this, passing the VBO filename as an argument
#

import collections
import csv
import re
import sys
import click
import colorama
from numpy import *
import matplotlib.pyplot as plt

class VBoxData:
    """
    A class representing the data read from a .VBO file.
    """
    def __init__(self, from_vbo_file=None):
        """
        Initialise instance, optionbally reading data from
        VBO file object.

        The 'data' field will be populated with a list of namedtuples,
        each of which has float fields based on the column names. So you can
        get, for example, self.data[0].velocity.
        """
        self.creation_date = None
        self.comments = []
        self.headers = []
        self.column_names = []
        self.data = []

        if from_vbo_file:
            # Crude parser
            section = None
            for raw_line in from_vbo_file:
                line = raw_line.strip()

                # Start of new section
                m = re.match(r'\[([\s\w)]+)\]', line)
                if m is not None:
                    section = m.group(1)

                else:
                    # We're within a section
                                    
                    if (section is None) and line.startswith('File created on'):
                        # Will parse this at some point
                        self.creation_date = line[16:]

                    if line and (section == 'header'):
                        self.headers.append(line)

                    if line and (section == 'comments'):
                        self.comments.append(line)

                    if line and (section == 'column names'):
                        # To use the columns as field names in named tuples, we need to replace hyphens
                        self.column_names = [c.replace('-','_') for c in line.split()]
                        self.column_name_map = dict([k[::-1] for k in enumerate(self.column_names)])
                        assert(self.column_names[1] == 'time') # We assume this later
                        VBoxDataTuple = collections.namedtuple('VBoxDataTuple', self.column_names)

                    if line and (section == 'data'):
                        # I think data fields are always numbers, but in different formats
                        # We'll treat them as floats for now
                        bits = line.split()
                        fields = [float(f) for f in bits]

                        # Time, however, looks like a float but is HHMMSS.SS
                        tstamp = bits[1]
                        (hrs, mins, secs) = int(tstamp[0:2]), int(tstamp[2:4]), float(tstamp[4:])
                        fields[1] = 3600 * hrs + 60 * mins + secs

                        # We assume that time=000000.00 indicates the start of useful data
                        if fields[1] == 0.0:
                            self.data = []
                        tup = VBoxDataTuple(*fields)
                        self.data.append(tup)


@click.command
def main():
    with open(sys.argv[1]) as f:
        v1 = VBoxData(f)

    print len(v1.data),"points"
    # Dump as CSV
    # csv_out =csv.writer(sys.stdout)
    # csv_out.writerow(v1.column_names)
    # for d in v1.data:
    #     csv_out.writerow(d)

    # Playing with NumPy
    # a = array(v1.data)
    # b = a.transpose()
    # plt.plot(b[v1.column_name_map['time']], b[v1.column_name_map['PedalPos_CH']])
    # plt.plot(b[v1.column_name_map['time']], b[v1.column_name_map['BrakePressure_HS1_CH']])
    # plt.plot(b[v1.column_name_map['time']], b[v1.column_name_map['VehicleSpeed_HS1_CH']])
    # plt.show()

    if False:
        plt.figure(1)

        plt.subplot(211)
        plt.title('Accelerator, brake and speed')
        accel_line, brake_line, speed_line = plt.plot(
            [d.time for d in v1.data],   # x axis
            [(d.PedalPos_CH, d.BrakePressure_HS1_CH, d.VehicleSpeed_HS1_CH ) for d in v1.data]  # y values
        )
        plt.legend([accel_line, brake_line, speed_line], ['Accel', 'Brake', 'Speed'])

        plt.subplot(212)
        plt.title('Steering')
        plt.xlabel('Time (s)')
        steering_line, indicator_line = plt.plot(
            [d.time for d in v1.data],   # x axis
            [(d.SteeringWheelAngle_CH, [0, -100, 100][int(d.DirectionIndicationSwitchHS_CH)]) for d in v1.data]  # y values
        )
        plt.axhline()
        plt.ylabel('Deg left')
        plt.legend([steering_line, indicator_line], ['Steering','Indicator'])

        plt.show()

    plt.figure(2)
    plt.title('Track')
    ax = plt.gca()
    ax.set_axis_bgcolor((0,0,0))
    max_vel = max([d.velocity for d in v1.data])
    prev_lat, prev_lon = None, None
    for d in v1.data[::10]:
        vel_norm = d.velocity/max_vel
        # lat and long appear to be in minutes N & W
        lat, lon = d.lat/60.0, -d.long/60.0
        if prev_lat is not None:
            track_pt = plt.plot(
                [prev_lon, lon], [prev_lat, lat],
                color=(vel_norm,0.4,1.0-vel_norm,1)
            )
        prev_lat, prev_lon = lat, lon
    # Coventry label    
    plt.plot(-1.510948, 52.407762, marker='+', color='white') # Coventry
    plt.annotate('Coventry', xy=(-1.510948, 52.407762), xytext=(-1.509, 52.408), color='gray')
    # Warwick label
    plt.plot( -1.5626, 52.3838, marker='+', color='white')
    plt.annotate('Warwick Uni', xy=( -1.5626, 52.3838), xytext=( -1.5616, 52.3848,), color='gray')
    plt.show()

if __name__ == '__main__':
    main()