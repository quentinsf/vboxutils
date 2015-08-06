#! /usr/bin/env python

import datetime
import glob
import os
import sys
import json

from flask import Flask, render_template, request, redirect, url_for
from werkzeug import secure_filename

from vbox import VBoxData, TimeEncoder

app = Flask(__name__)
GOOGLE_API_BROWSER_KEY="AIzaSyBci7wj9yFLcf5SHEmwXFXvWxbg97oSxYQ"

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['vbo'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """
    Check filename has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            new_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(new_name)

            # process uploaded VBO file
            with open(new_name) as f:
                vbox_data = VBoxData(f)
            center_lat = (vbox_data.max_lat + vbox_data.min_lat)/2.0
            center_long = (vbox_data.max_long + vbox_data.min_long)/2.0
            map_options = {
                  "center": { "lat": center_lat, "lng": center_long},
                  "zoom": 12
            }
            marker = {
                "position": {"lat": vbox_data.data[0].lat, "lng": vbox_data.data[0].long},
                "title": "Start"
            }
            # Make GeoJSON file            
            json_name = new_name.rsplit('.')[0] + ".json"
            with open(json_name, 'w') as outf:
                vbox_data.write_geojson(outf)

            html_filename =  new_name.rsplit('.')[0] + ".html"
            with open(html_filename, 'w') as outf:
                outf.write(
                    render_template('route.html', vbd=vbox_data, title=filename, 
                        json_url = os.path.basename(json_name),
                        api_key=GOOGLE_API_BROWSER_KEY, map_options=map_options, marker=marker)
                )
            return redirect(html_filename)

    else:
        routes = [
            os.path.basename(r).rsplit('.')[0] for r in glob.glob(os.path.join(UPLOAD_FOLDER, '*.vbo'))
        ]
        return render_template('home.html', routes=routes)
     
@app.route("/route/<routename>")
def route(routename):
    return redirect(os.path.join(app.config['UPLOAD_FOLDER'], routename + ".html"))

# Return the current route as GeoJSON.  
# Note that we just return one point in every 10.
@app.route("/about/")
def about():
    return  render_template('about.html')

if __name__ == '__main__':
    app.debug=True  # flask dbeugging and auto-reloading
    app.run(host='0.0.0.0')
