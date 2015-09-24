#! /usr/bin/env python
#
# Run this, passing the VBO filename as an argument.
# Specify one of the options to make it do something.
# --help will give you the details.
#
# Quentin Stafford-Fraser 2015


import click
import sys

from vbox import VBoxData


# Click is a handy way to parse command-line arguments:  http://click.pocoo.org
@click.command()
@click.option('--graph', '-r', default=False, is_flag=True, help="Draw a pretty plot")
@click.option('--track', '-t', default=False, is_flag=True, help="Draw a map")
@click.option('--gpx',   '-p', default=None, type=click.File('w'), help="Output a GPX file")
@click.option('--csv',   '-c', default=None, type=click.File('w'), help="Output a CSV file")
@click.option('--geo',   '-g', default=None, type=click.File('w'), help="Output a GeoJSON file")
@click.argument('vbo_file', type=click.File('r'))

def main(graph, track, gpx, csv, geo, vbo_file):
    vbd = VBoxData(vbo_file)
    print >>sys.stderr, len(vbd.data),"points"

    if gpx:
        vbd.write_gpx(gpx)

    if csv:
        vbd.write_csv(csv)

    if geo:
        vbd.write_geojson(geo)

    if graph:
        vbd.plot_graph()

    if track:
        vbd.plot_track()


if __name__ == '__main__':
    main()