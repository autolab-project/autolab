# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 17:11:57 2019

@author: qchat
"""

import os

VERSION = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'version.txt')

USER_FOLDER = os.path.join(os.path.expanduser('~'),'autolab')
USER_LAST_CUSTOM_FOLDER = os.path.expanduser('~')
DEVICES_CONFIG = os.path.join(USER_FOLDER,'devices_config.ini')
AUTOLAB_CONFIG = os.path.join(USER_FOLDER,'autolab_config.ini')
PLOTTER_CONFIG = os.path.join(USER_FOLDER,'plotter_config.ini')

# Drivers locations
DRIVERS = os.path.join(USER_FOLDER,'drivers')
DRIVER_LEGACY = {'official':os.path.join(os.path.dirname(os.path.dirname(__file__)),'drivers'),
                  'local':os.path.join(USER_FOLDER,'local_drivers')}
DRIVER_SOURCES = {'official':os.path.join(DRIVERS,'official'),
                  'local':os.path.join(DRIVERS,'local')}

# Driver github repo
DRIVER_GITHUB = {'official':'https://github.com/autolab-project/autolab-drivers'}
