# VBOX experiments

The `vboxread` script can read the .VBO format files produced by a RaceLogic VBOX and perform a few operations on the data.

It will perform a couple of conversions on the data:

* The time, which is in the VBOX file as HHMMSS.SSS, will be converted to two extra fields:
    * time_of_day : time since midnight in seconds
    * timestamp: absolute seconds since the epoch, assuming this time is on the same day as the creation time recorded in the file. This makes sense as long as a GPS is connected and gives us this.
    * datetime: timestamp as a human-readable string

* Latitude and longitude are in the VBOX file as minutes, with west being positive. This script converts them to degrees, with east as positive:
    - lat_deg
    - long_deg 

Initially, it was expected that vboxread would nede to do a wide variety of tasks, but we're now primarily using it to convert to CSV and then processing CSV files with other tools.

## Basic use

Run

    vboxread --help

for the options.  Filenames can generally be specified as '-' if you want to use stdin/stdout. You can also specify more than one option at a time, for example:

    vboxread --graph --csv my.csv my.vbo

This will plot a graph and output a CSV file of the data.

Sometimes, it can be useful to make sure, regardless of timing and parking arrangements, that different journeys begin and end from the same place.  
The `vboxtrim` utility reads and writes CSV files, and takes optional arguments specifying a 'start zone' and 'end zone', each specified as long,lat,radius.  The output file will begin at the point where the track first leaves the start zone and finish at the point where it first enters the end zone.

For example:

    vboxtrim -s -1.56528,52.38286,300 -e -1.50707,52.408,300 \
        -o trimmed.csv route.csv

will output the bits of `route.csv` which start more than 300m from the Kirby Corner roundabout and will finish 300m from Coventry Cathedral.  It will save it to `trimmed.csv` If you have matplotlib installed, add `--graph` to see the effect.

If a start or end point is not specified, the beginning or end of the file will be used.  But if they *are* specified and the track does not pass through them, `vboxtrim` will exit with an error unless the -k option is specified. 

Since we expect to do most manipulations with these CSV files, it's useful to have a way to view the results on a map.  Google Earth and many other systems can view GPX files, which you can create from a CSV with `vboxcsv2gpx`:

    vboxcsv2gpx -o trimmed.gpx trimmed.csv

Many of these utilities will output to stdout if no output file is specified.

The experimental `vboxsvr` script will create a webserver on port 5000 that can take uploads of .VBO tracks and serve them up overlaid on a Google map.  

    vboxsrv



## Installation

On Linux, you may need to:

    apt-get install python-dev python-pip

first if you don't have much of a Python environment set up.

Then, if you just want to install the current version with minimal extra effort, try:

    pip install https://github.com/quentinsf/vboxutils/archive/master.zip

This includes some basic dependencies which allow it to make CSV, JSON and GPX files.  If you want to do more, you may need to install some other python packages.

    pip install -r requirements.txt

You may not need everything in requirements.txt if, say, you don't want to plot any graphs.

Then:

    pip install .



## Mac OS X install

On a Mac, you can use the built-in matplotlib and numpy or one of the binary installers, but if you want to run entirely in a virtualenv, you'll need to follow more complex instructions such as these to build matplotlib etc:

http://www.lowindata.com/2013/installing-scientific-python-on-mac-os-x/

A simpler alternative is to build your virtualenv allowing access to the system packages:

    virtualenv --system-site-packages env
    . env/bin/activate
    pip install -r requirements.txt


## VBO format

Some information available [here][1].


[1]: https://racelogic.support/01VBOX_Automotive/01VBOX_data_loggers/VBOX_3i_Range/Knowledge_base/VBO_file_format