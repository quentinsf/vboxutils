# VBOX experiments

# Mac OS X install

On a Mac, you can use the built-in matplotlib and numpy or one of the binary installers, but if you want to run entirely in a virtualenv, you'll need to follow more complex instructions such as these to build matplotlib etc:

http://www.lowindata.com/2013/installing-scientific-python-on-mac-os-x/

A simpler alternative is to build your virtualenv allowing access to the system packages:

    virtualenv --system-site-packages env
    . env/bin/activate
    pip install -r requirements.txt

# VBO format

Some information available [here][1].


[1]: https://racelogic.support/01VBOX_Automotive/01VBOX_data_loggers/VBOX_3i_Range/Knowledge_base/VBO_file_format