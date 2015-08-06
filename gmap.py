#! /usr/bin/env python

import datetime
import glob
import os
import sys
import json
import pandas as pd
from jinja2 import Environment, FileSystemLoader

GOOGLE_API_BROWSER_KEY="AIzaSyBci7wj9yFLcf5SHEmwXFXvWxbg97oSxYQ"

class GoogleMap(object):
    def __init__(self, dataframe, json_url=None, lat_name='lat', long_name='long'):
        self.data = dataframe
        self.lat_name = lat_name
        self.long_name = long_name
        # For convenience, though it's often handy to keep use
        # them in the main dataframe
        self.lats = self.data[self.lat_name]
        self.longs = self.data[self.long_name]
        self.json_url = json_url

    def to_html(self):
        """
        Output HTML for inclusion in iPython notebook.
        """
        center_lat = (self.lats.min() + self.lats.max())/2.0
        center_long = (self.longs.min() + self.longs.max())/2.0
        map_options = {
              "center": { "lat": center_lat, "lng": center_long},
              "zoom": 12
        }
        marker = {
            "position": {"lat": self.lats[0], "lng": self.longs[0]},
            "title": "Start"
        }

        # Build a geojson feature collection - need a more efficient way
        if self.json_url:
            geojson = None
        else:
            features = []
            prev_lat, prev_long = None, None
            for ts,p in self.data.iterrows():
                if prev_lat:
                    features.append(
                           { "type": "Feature", 
                             "geometry": { "type": "LineString", "coordinates": [[ prev_long, prev_lat ], [ p.long, p.lat ]] },
                             "properties": { "time": p.time }# p._asdict()
                           }
                        )
                prev_lat, prev_long = p.lat, p.long
            root = { "type": "FeatureCollection", "features": features }
            geojson = json.dumps(root)

        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('embedded_route.html')
        return template.render( data=self.data, 
            geojson=geojson, json_url=self.json_url,   # one or the other
            lat_name=self.lat_name, long_name = self.long_name,
            title="test",
            api_key=GOOGLE_API_BROWSER_KEY, 
            map_options=json.dumps(map_options), 
            marker=json.dumps(marker))
