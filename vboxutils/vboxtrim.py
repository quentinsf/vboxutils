#! /usr/bin/env python
#
# vboxtrim tries to ignmore all the fussing around that people might do
# at the beginning and end of a journey, and give us consistent routes
# starting and finishing when people leave a certain location and arrive 
# at another.
# 
# This takes in a CSV file and optional start and end zones.
# Zones are circles: a long & lat in degrees and a radius in metres.
# It will output a CSV file which is truncated at the beginnning until the 
# track has been inside and then left the start zone, and at the end until
# it enters the end zone.
#
# --help will give you the details.
#
# Quentin Stafford-Fraser 2015


import click
import sys
import pandas as pd
import numpy as np

def haversine(long1, lat1, long2, lat2):
    """ 
    Calculate distance using Haversine formula.
    Inputs can be scalars or series, and are in degrees.
    """
    R = 6371000 # Earth radius in metres
    long1_rad = np.deg2rad(long1)
    lat1_rad  = np.deg2rad(lat1)
    long2_rad = np.deg2rad(long2)
    lat2_rad  = np.deg2rad(lat2)
    dlong_rad = long2_rad - long1_rad
    dlat_rad  = lat2_rad - lat1_rad
    a = np.sin(dlat_rad/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlong_rad/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return c * R

# Click is a handy way to parse command-line arguments:  http://click.pocoo.org
@click.command()
@click.option('--start', '-s', default=None, help="Start zone: long,lat,dist")
@click.option('--end',   '-e', default=None, help="End zone: long,lat,dist")
@click.option('--out',   '-o', default=sys.stdout, type=click.File('w'), help="Output file")
@click.option('--graph', '-r', default=False, is_flag=True, help="Draw a pretty plot using matplotlib")
@click.argument('csv_file', type=click.File('r'))

def main(start, end, out, graph, csv_file):

    # Parse start and end zone specifications
    if start:
        start_bits = start.split(',')
        if len(start_bits) != 3:
            print >>sys.stderr, "Zones should be long,lat,dist - comma-separated without spaces"
            sys.exit(1)
        start_long, start_lat, start_dist = map(float, start_bits)
    
    if end:
        end_bits = end.split(',')
        if len(end_bits) != 3:
            print >>sys.stderr, "Zones should be long,lat,dist - comma-separated without spaces"
            sys.exit(1)
        end_long, end_lat, end_dist = map(float, end_bits)

    # OK - read the CSV file
    data = pd.read_csv(csv_file)
    print >>sys.stderr, "Reading %s points" % data.shape[0]

    start_idx = 0
    if start:
        # We work out how far each point is from the start.
        from_start = haversine(start_long, start_lat, data.long_deg, data.lat_deg)
        # Our start index is the first point where we move from inside to outside
        # the start zone, ie. where the previous point was less than start_dist and
        # the current one is greater or equal.
        start_point  = data[(from_start.shift() < start_dist) & (from_start >= start_dist)].head(1)
        if start_point.empty:
            print >>sys.stderr, "WARNING - no start point found"
        else:
            start_idx = start_point.index.tolist()[0]

    data_after_start = data[start_idx:]
    end_idx = -1
    if end:
        # We work out how far each point is from the end.
        from_end = haversine(end_long, end_lat, data_after_start.long_deg, data_after_start.lat_deg)
        # Our end index is the first point where we move from outside to inside
        # the end zone, ie. where the previous point was more than end_dist and
        # the current one is less than or equal.
        end_point  = data_after_start[(from_end.shift() > end_dist) & (from_end < end_dist)].head(1)
        if end_point.empty:
            print >>sys.stderr, "WARNING - no end point found"
        else:
            end_idx = end_point.index.tolist()[0] - start_idx
            # from_end[0:end_idx].plot()


    active_data = data_after_start.head(end_idx)
    print >>sys.stderr, "Writing %s points" % active_data.shape[0]
    active_data.to_csv(out, index=False)

    if graph:
        from matplotlib import pyplot as plt
        plt.plot(data.long_deg, data.lat_deg, 'k', linewidth=4)
        plt.plot(active_data.long_deg, active_data.lat_deg, 'r', linewidth=2)
        if start:
            plt.plot(start_long, start_lat, 'go', markersize=12)
        if end:
            plt.plot(end_long, end_lat, 'ro', markersize=8)
        plt.show()

if __name__ == '__main__':
    main()
