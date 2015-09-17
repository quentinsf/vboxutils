#!/usr/bin/env python

from setuptools import setup

setup(
    name="vboxutils",
    packages = ['vboxutils'],
    entry_points = {
        'console_scripts': [
            'vboxread = vboxutils.vboxread:main',
            'vboxsrv = vboxutils.de:main',
        ]
    },
    version = "0.1",
    description = "Read RaceLogic VBOX .VBO files",
    author = "Quentin Stafford-Fraser",
    author_email = "quentin@pobox.com",
    url = "http://github.com/quentinsf/vboxutils",
    install_requires = [
        'click',
        'jinja2'
    ],
    download_url = 'https://github.com/quentinsf/vboxutils/tarball/0.1',
    keywords = 'gis'
)
