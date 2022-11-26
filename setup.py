#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.8.3'

setup(
    name='ubi_reader',
    version=version,
    description='Extract files from UBI and UBIFS images.',
    author='Jason Pruitt',
    author_email='jrspruitt@gmail.com',
    url='https://github.com/jrspruitt/ubi_reader',
    long_description='Python tool for reading information about and extracting data from UBI and UBIFS images.',
    platforms=['Linux'],
    license='GNU GPL',
    keywords='UBI UBIFS',
    requires=['lzo'],
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            'ubireader = __main__:main',
        ]
    }
)
