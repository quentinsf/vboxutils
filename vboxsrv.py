#! /usr/bin/env python

from flask import Flask, render_template

from vbox import VBoxData

import sys

app = Flask(__name__)
GOOGLE_API_BROWSER_KEY="AIzaSyBci7wj9yFLcf5SHEmwXFXvWxbg97oSxYQ"


@app.route("/")
def home():
    center_lat = (app.vbox_data.max_lat + app.vbox_data.min_lat)/2.0
    center_long = (app.vbox_data.max_long + app.vbox_data.min_long)/2.0
    map_options = {
          "center": { "lat": center_lat, "lng": center_long},
          "zoom": 12
    }
    marker = {
        "position": {"lat": app.vbox_data.data[0].lat, "lng": app.vbox_data.data[0].long},
        "title": "Start"
    }
    return render_template('home.html', vbd=app.vbox_data, title=app.title, 
        api_key=GOOGLE_API_BROWSER_KEY, map_options=map_options, marker=marker)

# Return the current route as GeoJSON.  
# Note that we just return one point in every 10.
@app.route("/route.json")
def geojson():
    import json
    prev_p = None
    features = []
    for p in app.vbox_data.data[::10]:
        if prev_p:
            features.append(
               { "type": "Feature", 
                 "geometry": { "type": "LineString", "coordinates": [[ prev_p.long, prev_p.lat ], [ p.long, p.lat ]] },
                 "properties": { 
                    "color": "rgb({r},{g},{b})".format(
                        r=int(255*p.velocity/app.vbox_data.max_velocity),  
                        g=0,  
                        b=255-int(255*p.velocity/app.vbox_data.max_velocity)),
                    "weight": p.PedalPos_CH,
                 }
               }
            )
        prev_p = p
    root = { "type": "FeatureCollection", "features": features }
    return json.dumps(root)

if __name__ == '__main__':
    filename = sys.argv[1]
    with open(filename, 'r') as vbox_file:
        app.debug=True  # flask dbeugging and auto-reloading
        app.title = filename
        print "Reading",filename
        app.vbox_data = VBoxData(vbox_file)
        print "Ready: ", len(app.vbox_data.data), "points loaded"
        app.run(host='0.0.0.0')
