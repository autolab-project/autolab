# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 15:23:05 2020

@author: qchat
"""

import os

# Version file
VERSION = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'version.txt')

# Autolab directory in user home
USER_FOLDER = os.path.join(os.path.expanduser('~'),'autolab')
DEVICES_CONFIG = os.path.join(USER_FOLDER,'devices_config.ini')
AUTOLAB_CONFIG = os.path.join(USER_FOLDER,'autolab_config.ini')

# Drivers locations
DRIVER_SOURCES = {'main':os.path.join(os.path.dirname(os.path.dirname(__file__)),'drivers'),
                  'local':os.path.join(USER_FOLDER,'local_drivers')}

# User interaction
USER_LAST_CUSTOM_FOLDER = os.path.expanduser('~')

