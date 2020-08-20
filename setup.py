#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.7.0'

setup(
    name='ubi_reader',
    version=version,
    description='Extract files from UBI and UBIFS images.',
    author='Jason Pruitt',
    author_email='jrspruitt@gmail.com',
    url='https://github.com/jrspruitt/ubi_reader',
    long_description='Collection of Python scripts for reading information about and extracting data from UBI and UBIFS images.',
    platforms=['Linux'],
    license='GNU GPL',
    keywords='UBI UBIFS',

    requires=['lzo'],
    packages = find_packages(),
    scripts=['scripts/ubireader_display_info',
             'scripts/ubireader_extract_files',
             'scripts/ubireader_list_files',
             'scripts/ubireader_extract_images',
             'scripts/ubireader_utils_info',
             'scripts/ubireader_display_blocks',
            ],
)
