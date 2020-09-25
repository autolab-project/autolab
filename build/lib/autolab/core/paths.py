# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 17:11:57 2019

@author: qchat
"""

import os 

USER_FOLDER = os.path.join(os.path.expanduser('~'),'autolab')
USER_LAST_CUSTOM_FOLDER = os.path.expanduser('~')
LOCAL_CONFIG = os.path.join(USER_FOLDER,'local_config.ini')
AUTOLAB_CONFIG = os.path.join(USER_FOLDER,'autolab_config.ini')
LOCAL_CONFIG_TEMPLATE = os.path.join(os.path.dirname(__file__),'local_config.ini')
        
DRIVER_SOURCES = {'main':os.path.join(os.path.dirname(os.path.dirname(__file__)),'drivers'),
                  'local':os.path.join(USER_FOLDER,'local_drivers')}