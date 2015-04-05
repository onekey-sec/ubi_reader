#!/usr/bin/env python

from setuptools import setup,find_packages

version = '0.4'

setup(
    name='ubi_reader',
    version=version,
    description='',
    author='Jason Pruitt',
    url='https://github.com/jrspruitt/ubi_reader',
    license='GNU GPL',

    requires=['lzo'],
    packages = find_packages(),
    scripts=['scripts/ubireader_display_info',
             'scripts/ubireader_extract_files',
             'scripts/ubireader_extract_images',
             'scripts/ubireader_utils_info'
            ],
)
