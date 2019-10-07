# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 17:11:57 2019

@author: qchat
"""

import os 

class Paths :
    
    def __init__(self) :
            
        self.DRIVERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),'drivers')
        self.USER_FOLDER_PATH = os.path.join(os.path.expanduser('~'),'autolab')
        self.USER_LAST_CUSTOM_FOLDER_PATH = os.path.expanduser('~')
        self.DEVICES_INDEX_PATH = os.path.join(self.USER_FOLDER_PATH,'devices_index.ini')
        self.TEMPLATE_FILES_PATH = os.path.dirname(__file__)