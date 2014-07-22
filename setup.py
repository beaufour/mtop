#!/usr/bin/env python

from setuptools import setup
setup(
    name='mtop',
    version='0.4',
    url='https://github.com/beaufour/mtop',
    author='Allan Beaufour',
    author_email='allan@beaufour.dk',
    description='mtop is a top like tool for MongoDB.',
    zip_safe=False,
    packages=['mtop', 'mtop.lib'],
    install_requires=[
        'pymongo'
    ],
    entry_points = {
        'console_scripts': [
            'mtop = mtop.main:main'
        ],
    }
)
