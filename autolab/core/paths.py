# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 17:11:57 2019

@author: qchat
"""

import os 

DRIVERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),'drivers')
USER_FOLDER_PATH = os.path.join(os.path.expanduser('~'),'usit')
USER_LAST_CUSTOM_FOLDER_PATH = os.path.expanduser('~')
DEVICES_INDEX_PATH = os.path.join(USER_FOLDER_PATH,'devices_index.ini')
TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__),'files')