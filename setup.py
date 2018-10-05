#!/usr/bin/env python3
from setuptools import setup
from pymonitor import __version__

setup(name='pymonitor',
    version=__version__,
    description='python daemon for logging system metrics to elasticsearch db',
    url='http://gitlab.xmopx.net/dave/python-esmonitor',
    author='dpedu',
    author_email='dave@davepedu.com',
    packages=['pymonitor', 'pymonitor.builtins', 'pymonitor.monitors'],
    entry_points={
        "console_scripts": [
            "pymonitor = pymonitor.daemon:main"
        ]
    },
    zip_safe=False)
