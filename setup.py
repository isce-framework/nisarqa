#!/usr/bin/env python3
# NISAR Project - Jet Propulsion Laboratory 
# Copyright 2022, by the California Institute of Technology.
# ALL RIGHTS RESERVED. United States Government Sponsorship acknowledged.
# This software may be subject to U.S. export control laws and regulations.

import glob
import os

from setuptools import Command, find_packages, setup


class CleanCommand(Command):
    '''Custom clean command to tidy up the project root.'''
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        # Make sure to remove the .egg-info file 
        os.system('rm -vrf .scratch_dir ./build ./dist ./*.pyc ./*.tgz ./*.egg-info ./src/*.egg-info')

setup(
    name = 'nisarqa',
    maintainer = 'NISAR ADT Team',
    maintainer_email = 'samantha.c.niemoeller@jpl.nasa.gov',
    description = 'NISAR ADT Quality Assurance',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',    
    license = 'Copyright by the California Institute of Technology.'
                'All rights reserved',
    url = 'http://nisar.jpl.nasa.gov',
    version = '3.0.1',

    # Gather all packages located under `src`.
    # (A package is a directory containing an __init__.py file.)
    package_dir={ '' : 'src'},
    packages=find_packages(where='src'),

    test_suite = 'tests',

    entry_points = { 
        "console_scripts" :
            ["nisarqa = nisarqa.__main__:main"]
        },

    data_files=[( 'product_specs',
                   glob.glob(os.path.join('src', 'parameters', 'product_specs', '*.xml' )))],
    
    install_requires=['setuptools', 
                      'numpy',
                      'h5py',
                      'pytest',
                      'pillow',
                      'ruamel.yaml',
                      'yamale',
                      'cycler',
                      'matplotlib',
                      'scipy'
                      ],
    cmdclass={
        'clean': CleanCommand,
        }
)
    
