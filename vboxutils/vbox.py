#! /usr/bin/env python
#
# Run this, passing the VBO filename as an argument.
# Specify one of the options to make it do something.
# --help will give you the details.
#

import collections
import csv
import json
import re
import sys
import time
from datetime import datetime

import logging
logging.basicConfig()
log=logging.getLogger(__name__)

# By default, the JSON package doesn't encode datetimes.
class TimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

# Here's a Jinja template for creating a GPX file
GPX_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<gpx
  version="1.0"
  creator="vboxread"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/0"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
<time>{{vboxdata.creation_date.strftime('%Y-%m-%dT%H:%M:%SZ')}}</time>
<bounds minlat="{{vboxdata.min_lat}}" minlon="{{vboxdata.min_long}}" maxlat="{{vboxdata.max_lat}}" maxlon="{{vboxdata.max_long}}"/>
<trk>
  <trkseg>
    {% for p in vboxdata.data %}
    <trkpt lat="{{p.lat_deg}}" lon="{{p.long_deg}}">
      <ele>{{p.height}}</ele>
      <time>{{p.datetime.strftime('%Y-%m-%dT%H:%M:%SZ')}}</time>
      <course>{{p.heading}}</course>
      <speed>{{p.velocity}}</speed>
      <sat>{{p.sats}}</sat>
    </trkpt>
    {% endfor %}
  </trkseg>
</trk>
</gpx>
"""

class VBoxData:
    """
    A class representing the data read from a .VBO file.
    """
    def __init__(self, from_vbo_file=None):
        """
        Initialise instance, optionally reading data from
        VBO file object.

        The 'data' field will be populated with a list of namedtuples,
        each of which has float fields based on the column names. So you can
        get, for example, self.data[0].velocity.

        Future optimisation if needed: we could slice the data more efficiently
        by making it a NumPy array rather than a list of named tuples.
        """
        self.creation_date = None
        self.creation_midnight = None
        self.comments = []
        self.headers = []
        self.column_names = []
        self.data = []
        if from_vbo_file:
            self.read_vbo(from_vbo_file)


    def read_vbo(self, from_vbo_file):
        """
        Populate this object by reading the specified VBO file.

        from_vbo_file should be an open file-like object.
        """
        section = None
        # How many fields on a complete data input line?
        expected_fields = None
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
                    creation_date = line[16:]
                    self.creation_date = datetime.strptime(creation_date, "%d/%m/%Y @ %H:%M:%S")
                    self.creation_midnight = self.creation_date.replace(hour=0, minute=0, second=0, microsecond=0)

                if line and (section == 'header'):
                    self.headers.append(line)

                if line and (section == 'comments'):
                    self.comments.append(line)

                if line and (section == 'column names'):
                    # To use the columns as field names in named tuples, we need to replace hyphens
                    self.column_names = [c.replace('-','_') for c in line.split()]
                    self.column_name_map = dict([k[::-1] for k in enumerate(self.column_names)])
                    assert(self.column_names[1] == 'time')  # We assume this later
                    assert(self.column_names[2] == 'lat')   # We assume this later
                    assert(self.column_names[3] == 'long')  # We assume this later
                    self.column_names.append('time_of_day') # time converted into secs
                    self.column_names.append('datetime')    # absolute time
                    self.column_names.append('timestamp')   # absolute time in secs
                    self.column_names.append('lat_deg')     # latitude in degrees
                    self.column_names.append('long_deg')    # longitude in degrees
                    VBoxDataTuple = collections.namedtuple('VBoxDataTuple', self.column_names)

                if line and (section == 'data'):
                    bits = line.split()
                    # Check we got the number of fields we expected - the last line
                    # can sometimes be truncated.
                    if expected_fields is None: 
                        expected_fields=len(bits)
                    if len(bits) != expected_fields:
                        log.warning('Skipping a data line which does not include %s fields', expected_fields)
                        continue

                    # I think data fields are always numbers, but in different formats
                    # We'll treat them as floats for now

                    fields = [float(f) for f in bits]

                    # Time, however, looks like a float but is HHMMSS.SS
                    tstamp = bits[1]
                    (hrs, mins, secs) = int(tstamp[0:2]), int(tstamp[2:4]), float(tstamp[4:])
                    # Add a new field with the time in seconds from midnight
                    fields.append(3600 * hrs + 60 * mins + secs)
                    # We turn it into an absolute timestamp by offsetting the time 
                    # from midnight on the creation date.
                    absolute_time = self.creation_midnight.replace(hour = hrs, minute=mins, second=int(secs))
                    fields.append( absolute_time )
                    fields.append(  time.mktime(absolute_time.timetuple()) )

                    # And lat and long are in minutes, with west as positive
                    # Convert to conventional degrees as lat_deg and long_deg
                    fields.append( float(fields[2])/60.0 )
                    fields.append( -1 * float(fields[3])/60.0 )

                    # If there's no GPS signal, we won't have absolute time.
                    # We assume that time=000000.00 indicates the start of useful data.
                    # (This comes from an early test file where the first few records
                    # were at 23:59:xx.xxx.)
                    if fields[1] == 0.0:
                        self.data = []

                    tup = VBoxDataTuple(*fields)
                    self.data.append(tup)

        self.min_lat = min([d.lat_deg for d in self.data])
        self.max_lat = max([d.lat_deg for d in self.data])
        self.min_long = min([d.long_deg for d in self.data])
        self.max_long = max([d.long_deg for d in self.data])
        self.max_velocity = max([d.velocity for d in self.data])


    def write_csv(self, outfile=sys.stdout):
        """
        Create a CSV file of the data fields.

        out_file should be an open file-like object.
        """
        csv_out =csv.writer(outfile)
        csv_out.writerow(self.column_names)
        for d in self.data:
            csv_out.writerow(d)


    def plot_graph(self):
        """
        Plot some interesting things on a graph.
        """

        import matplotlib.pyplot as plt

        plt.figure(1)

        plt.subplot(211)
        plt.title('Accelerator, brake and speed')
        accel_line, brake_line, speed_line = plt.plot(
            [d.time_of_day for d in self.data],   # x axis
            [(d.PedalPos_CH, d.BrakePressure_HS1_CH, d.VehicleSpeed_HS1_CH ) for d in self.data]  # y values
        )
        plt.legend([accel_line, brake_line, speed_line], ['Accel', 'Brake', 'Speed'])

        plt.subplot(212)
        plt.title('Steering')
        plt.xlabel('Time (s)')
        steering_line, indicator_line = plt.plot(
            [d.time_of_day for d in self.data],   # x axis
            [(d.SteeringWheelAngle_CH, [0, -100, 100][int(d.DirectionIndicationSwitchHS_CH)]) for d in self.data]  # y values
        )
        plt.axhline()
        plt.ylabel('Deg left')
        plt.legend([steering_line, indicator_line], ['Steering','Indicator'])

        plt.show()


    def plot_track(self):
        """
        Plot location and colour with speed.
        """
        import matplotlib.pyplot as plt
        from matplotlib.transforms import ScaledTranslation

        fig = plt.figure()
        plt.title('Track')
        ax = plt.gca()
        ax.set_axis_bgcolor((0.1,0.1,0.1))
        max_vel = max([d.velocity for d in self.data])
        if max_vel == 0:
            click.echo("No movement detected!", err=True)
            sys.exit(1)

        plt.scatter(
            [d.long_deg for d in self.data],
            [d.lat_deg for d in self.data],
            c=[(d.velocity/max_vel,0.4,1.0-d.velocity/max_vel,1) for d in self.data],
            s=1,
            marker = u'.',
            linewidth=0, edgecolor='none'
        )
 
        plt.axis('equal')  # a degree is a degree

        labels = [
            ('Coventry', -1.510948, 52.407762),
            ('Warwick Uni', -1.5626, 52.3838),
        ]
        # Coventry label
        for l in labels:
            plt.plot(l[1], l[2], marker='+', color='white')
            plt.annotate(l[0], xy=(l[1], l[2]), 
                    xytext=(5,5), textcoords='offset points', color='gray', alpha=0.8)
        
        plt.show()


    def write_gpx(self, outfile=sys.stdout):
        # Get the Jinja template for rendering a GPX file
        import jinja2
        template = jinja2.Template(GPX_TEMPLATE)
        outfile.write( template.render(vboxdata = self) )


    def to_json(self, stride=10):
        """
        Convert every stride-th point to GeoJSON.
        """
        import json
        prev_p = None
        features = []
        for p in self.data[::stride]:
            if prev_p:
                features.append(
                   { "type": "Feature", 
                     "geometry": { "type": "LineString", "coordinates": [[ prev_p.long_deg, prev_p.lat_deg ], [ p.long_deg, p.lat_deg ]] },
                     "properties": p._asdict()
                   }
                )
            prev_p = p
        root = { "type": "FeatureCollection", "features": features }
        return json.dumps(root, cls=TimeEncoder, indent=2)


    def write_geojson(self, outfile=sys.stdout):
        outfile.write(self.to_json())


