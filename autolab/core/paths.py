# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 17:11:57 2019

@author: qchat
"""

import os

AUTOLAB_FOLDER = os.path.dirname(os.path.dirname(__file__))

VERSION = os.path.join(AUTOLAB_FOLDER, 'version.txt')

LAST_FOLDER = os.path.expanduser('~')
USER_FOLDER = os.path.join(os.path.expanduser('~'), 'autolab')
DEVICES_CONFIG = os.path.join(USER_FOLDER, 'devices_config.ini')
AUTOLAB_CONFIG = os.path.join(USER_FOLDER, 'autolab_config.ini')
PLOTTER_CONFIG = os.path.join(USER_FOLDER, 'plotter_config.ini')
HISTORY_CONFIG = os.path.join(USER_FOLDER, '.history_config.txt')

# Drivers locations
DRIVERS = os.path.join(USER_FOLDER, 'drivers')
DRIVER_LEGACY = {'official': os.path.join(AUTOLAB_FOLDER, 'drivers'),
                 'local': os.path.join(USER_FOLDER, 'local_drivers')}
# can add paths in autolab_config.ini [extra_driver_path]
DRIVER_SOURCES = {'official': os.path.join(DRIVERS, 'official'),
                  'local': os.path.join(DRIVERS, 'local')}

# Driver repository
# can add paths in autolab_config.ini [extra_driver_url_repo]
# format is {'path to install': 'url to download'}
DRIVER_REPOSITORY = {DRIVER_SOURCES['official']: 'https://github.com/autolab-project/autolab-drivers'}

PATHS = {'autolab_folder': AUTOLAB_FOLDER, 'version': VERSION,
         'user_folder': USER_FOLDER, 'drivers': DRIVERS,
         'devices_config': DEVICES_CONFIG, 'autolab_config': AUTOLAB_CONFIG,
         'plotter_config': PLOTTER_CONFIG, 'history_config': HISTORY_CONFIG,
         'last_folder': LAST_FOLDER}

# Storage of the drivers paths
DRIVERS_PATHS = {}
