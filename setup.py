#!/usr/bin/python
# -*- coding: UTF-8 -*-

import setuptools


def readme():
  with open('README.md', 'r') as f:
    return f.read()

setuptools.setup(
    name='spirentapi',
    version='1.2.4',
    author='Ding Yi',
    author_email='dvdface@hotmail.com',
    url='https://github.com/dvdface/spirentapi',
    description='wrapper to the Spirent TestCenter Tcl shell API(stc::, sth::)',
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=['spirentapi'],
    package_data={'spirentapi':['API.TXT']},
    install_requires=['python-dateutil'],
    tests_require= ['pytest', 'pytest-html', 'pytest-cov'],
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)