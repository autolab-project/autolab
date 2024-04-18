# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 17:11:57 2019

@author: qchat
"""

import os


AUTOLAB_FOLDER = os.path.dirname(os.path.dirname(__file__))

VERSION = os.path.join(AUTOLAB_FOLDER, 'version.txt')

USER_FOLDER = os.path.join(os.path.expanduser('~'), 'autolab')
USER_LAST_CUSTOM_FOLDER = os.path.expanduser('~')
DEVICES_CONFIG = os.path.join(USER_FOLDER, 'devices_config.ini')
AUTOLAB_CONFIG = os.path.join(USER_FOLDER, 'autolab_config.ini')
PLOTTER_CONFIG = os.path.join(USER_FOLDER, 'plotter_config.ini')
HISTORY_CONFIG = os.path.join(USER_FOLDER, '.history_config.txt')

# Drivers locations
DRIVERS = os.path.join(USER_FOLDER,'drivers')
DRIVER_LEGACY = {'official': os.path.join(AUTOLAB_FOLDER, 'drivers'),
                  'local': os.path.join(USER_FOLDER, 'local_drivers')}
# can add paths in autolab_config.ini [extra_driver_path]
DRIVER_SOURCES = {'official': os.path.join(DRIVERS, 'official'),
                  'local': os.path.join(DRIVERS, 'local')}

# Driver repository
# can add paths in autolab_config.ini [extra_driver_url_repo]
# format is {'path to install': 'url to download'}
DRIVER_REPOSITORY = {DRIVER_SOURCES['official']: 'https://github.com/autolab-project/autolab-drivers'}
