#! /usr/bin/env python
#
# vboxcsv2gpx
# 
# This takes in a CSV file and outputs a simple GPX file.
#
# --help will give you the details.
#
# Quentin Stafford-Fraser 2015


import click
import jinja2
import sys

import pandas as pd

# Here's a Jinja template for creating a GPX file
GPX_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<gpx
  version="1.0"
  creator="vboxcsv2gpx"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/0"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
<time>{{data.dt.min().strftime('%Y-%m-%dT%H:%M:%SZ')}}</time>
<bounds minlat="{{min_lat}}" minlon="{{min_long}}" maxlat="{{max_lat}}" maxlon="{{max_long}}"/>
<trk>
  <trkseg>
    {% for i,p in data.iterrows() %}
    <trkpt lat="{{p.lat_deg}}" lon="{{p.long_deg}}">
      <ele>{{p.height}}</ele>
      <time>{{p.dt.strftime('%Y-%m-%dT%H:%M:%SZ')}}</time>
      <course>{{p.heading}}</course>
      <speed>{{p.velocity}}</speed>
      <sat>{{p.sats}}</sat>
    </trkpt>
    {% endfor %}
  </trkseg>
</trk>
</gpx>
"""

# Click is a handy way to parse command-line arguments:  http://click.pocoo.org
@click.command()
@click.option('--out',   '-o', default=sys.stdout, type=click.File('w'), help="Output file")
@click.argument('csv_file', type=click.File('r'))

def main(out, csv_file):

    # OK - read the CSV file
    data = pd.read_csv(csv_file)
    print >>sys.stderr, "Reading %s points" % data.shape[0]

    data['dt'] = pd.to_datetime(data['datetime'])
    template = jinja2.Template(GPX_TEMPLATE)
    out.write( template.render(
        data = data, 
        min_lat  = data.lat_deg.min(), max_lat  = data.lat_deg.max(),
        min_long = data.long_deg.min(), max_long = data.long_deg.max(),
    ) )


if __name__ == '__main__':
    main()
