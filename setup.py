#!/usr/bin/python

import os
from setuptools import setup, find_packages
import InvoiceGenerator

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "InvoiceGenerator",
    version = InvoiceGenerator.__versionstr__,
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
        "reportlab", "PIL"
        ],
    package_data={'InvoiceGenerator': ['locale/cs/LC_MESSAGES/*']},
)
