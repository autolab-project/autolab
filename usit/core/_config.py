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
TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__),'files')


def checkConfig():

    # LOCAL FOLDER
    if os.path.exists(USER_FOLDER_PATH) is False :
        os.mkdir(USER_FOLDER_PATH)
        print(f'INFORMATION: The local folder USIT has been created : {USER_FOLDER_PATH}')
    
    # LOCAL CONFIG
    if os.path.exists(DEVICES_INDEX_PATH) is False :
        for filename in ['devices_index.ini','launcher.cmd','launcher.py'] :
            shutil.copyfile(os.path.join(TEMPLATE_FILES_PATH,filename),
                            os.path.join(USER_FOLDER_PATH,filename))

        print(f'INFORMATION: The configuration file devices_index.ini has been created : {USER_FOLDER_PATH}')
        


