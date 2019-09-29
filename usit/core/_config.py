# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 16:02:59 2019

@author: qchat
"""

import shutil
import os 

DRIVERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),'drivers')
USER_FOLDER_PATH = os.path.join(os.path.expanduser('~'),'usit')
USER_LAST_CUSTOM_FOLDER_PATH = os.path.expanduser('~')
DEVICES_INDEX_PATH = os.path.join(USER_FOLDER_PATH,'devices_index.ini')
DEVICES_INDEX_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__),'devices_index_template.ini')

def checkConfig():

    # LOCAL FOLDER
    if os.path.exists(USER_FOLDER_PATH) is False :
        os.mkdir(USER_FOLDER_PATH)
        print(f'INFORMATION: The local folder USIT has been created : {USER_FOLDER_PATH}')
    
    # LOCAL CONFIG
    if os.path.exists(DEVICES_INDEX_PATH) is False :
        shutil.copyfile(DEVICES_INDEX_TEMPLATE_PATH,USER_FOLDER_PATH)
        print(f'INFORMATION: The configuration file devices_index.ini has been created : {USER_FOLDER_PATH}')
        


