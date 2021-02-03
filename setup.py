#!/usr/bin/python
# -*- coding: UTF-8 -*-

import setuptools


def readme():
  with open('README.md', 'r') as f:
    return f.read()

setuptools.setup(
    name='spirentapi',
    version='1.0.0',
    author='Ding Yi',
    author_email='dvdface@hotmail.com',
    url='https://github.com/dvdface/spirentapi',
    description='wrapper to the Spirent stc::, sth:: api',
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=['spirentapi'],
    install_requires=['python-dateutil'],
    tests_require= ['pytest', 'pytest-html'],
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)