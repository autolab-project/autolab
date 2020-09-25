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

DRIVER_SOURCES = {'main':os.path.join(os.path.dirname(os.path.dirname(__file__)),'drivers'),
                  'local':os.path.join(USER_FOLDER,'local_drivers')}
