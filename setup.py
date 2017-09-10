#!/usr/bin/python

import os
import shlex
import subprocess
import sys

import InvoiceGenerator

from setuptools import find_packages, setup

version = InvoiceGenerator.__versionstr__

# release a version, publish to GitHub and PyPI
if sys.argv[-1] == 'publish':
    def command(cmd):
        subprocess.check_call(shlex.split(cmd))
    command('git tag v' + version)
    command('git push --tags origin master:master')
    command('python setup.py sdist upload')
    sys.exit()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


description = ''

for file_ in ('README', 'CHANGES', 'CONTRIBUTORS'):
    description += read('%s.rst' % file_) + '\n\n'


setup(
    name="InvoiceGenerator",
    version=version,
    author="Adam Strauch",
    author_email="cx@initd.cz",
    description="Library to generate PDF invoice.",
    license="BSD",
    keywords="invoice invoices generator",
    url="https://github.com/creckx/InvoiceGenerator",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    long_description=description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
        "reportlab",
        "pillow",
        "qrplatba>=0.3.3",
        'babel',
    ],
    tests_require=[
        "PyPDF2",
        "xmlunittest",
        "future",
    ],
    include_package_data=True,
    test_suite='tests',
    command_options={
        'build_sphinx': {
            'version': ('setup.py', version),
            'release': ('setup.py', version),
        },
    },
)
