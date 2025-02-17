#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Package version
__version__ = '0.1.0'

# Importing the main modules
from distributed_configuration_downloader import *