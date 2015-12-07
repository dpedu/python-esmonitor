#!/usr/bin/env python3
from setuptools import setup

__version__ = "0.0.1"

setup(name='pymonitor',
    version=__version__,
    description='python daemon for logging system metrics to elasticsearch db',
    url='http://gitlab.xmopx.net/dave/python-esmonitor',
    author='dpedu',
    author_email='dave@davepedu.com',
    packages=['pymonitor', 'pymonitor.builtins', 'pymonitor.monitors'],
    scripts=['bin/pymonitor'],
    zip_safe=False)
