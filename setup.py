#!/usr/bin/env python2
# coding:utf-8

import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "python-sid-player",
    version = "0.0.1",
    author = "Daniel Nögel",
    author_email = "github@post.noegelmail.de",
    description = ("Python SID player library based on gstreamer"),
    license = "MIT",
    keywords = "SID c64 player library gstreamer",
    packages=['sidplay'],
    #url = "http://packages.python.org/an_example_pypi_project",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)