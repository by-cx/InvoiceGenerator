#!/usr/bin/python

import os
import sys
import subprocess
import shlex
from setuptools import setup, find_packages
import InvoiceGenerator

version = InvoiceGenerator.__versionstr__

# release a version, publish to GitHub and PyPI
if sys.argv[-1] == 'publish':
    command = lambda cmd: subprocess.check_call(shlex.split(cmd))
    command('git tag v' + version)
    command('git push --tags origin master:master')
    command('python setup.py sdist upload')
    sys.exit()

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "InvoiceGenerator",
    version =version,
    author = "Adam Strauch",
    author_email = "cx@initd.cz",
    description = ("Library to generate PDF invoice."),
    license = "BSD",
    keywords = "invoice invoices generator",
    url = "https://github.com/creckx/InvoiceGenerator",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    long_description="This is library to generate simple PDF invoice. It's based on ReportLab.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
        "reportlab", "PIL", "qrplatba>=0.3.3"
        ],
    package_data={'InvoiceGenerator': ['locale/cs/LC_MESSAGES/*']},
)
