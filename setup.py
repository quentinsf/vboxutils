#!/usr/bin/env python

from setuptools import setup

VERSION="0.5"

setup(
    name="vboxutils",
    packages = ['vboxutils'],
    entry_points = {
        'console_scripts': [
            'vboxread = vboxutils.vboxread:main',
            'vboxsrv = vboxutils.vboxsrv:main',
            'vboxtrim = vboxutils.vboxtrim:main',
            'vboxcsv2gpx = vboxutils.vboxcsv2gpx:main',       
        ]
    },
    version = VERSION,
    description = "Read RaceLogic VBOX .VBO files",
    author = "Quentin Stafford-Fraser",
    author_email = "quentin@pobox.com",
    url = "http://github.com/quentinsf/vboxutils",
    install_requires = [
        'click',
        'jinja2',
        'pandas',
    ],
    download_url = 'https://github.com/quentinsf/vboxutils/tarball/%s' % VERSION,
    keywords = 'gis'
)
