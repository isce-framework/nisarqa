#!/usr/bin/env python3
# NISAR Project - Jet Propulsion Laboratory 
# Copyright 2019, by the California Institute of Technology.
# ALL RIGHTS RESERVED. United States Government Sponsorship acknowledged.
# This software may be subject to U.S. export control laws and regulations.

# setup.py: setup file for QualityAssurance library

from setuptools import setup, find_packages
import subprocess
import distutils

def configuration(parent_package="", top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path)
    config.set_options(ignore_setup_xxx_py=True, \
                       assume_default_configuration=True, \
                       delegate_options_to_subpackages=True, \
                       quiet=True)
    config.add_subpackage("quality")
    return config

from numpy.distutils.core import setup
setup(name = "quality",
    maintainer = "NISAR ADT Team",
    maintainer_email = "Catherine.M.Moroney@jpl.nasa.gov",
    description = "NISAR Quality Assurance",
    license = "All rights reserved",
    url = "http://nisar.jpl.nasa.gov",
    version = "V1.0",
    packages = ["quality"],
    test_suite = "test",
    configuration=configuration
)
    