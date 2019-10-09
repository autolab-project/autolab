# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 16:02:59 2019

@author: qchat
"""

import shutil
import os 

def check(paths):

    # LOCAL FOLDER
    if os.path.exists(paths.USER_FOLDER_PATH) is False :
        os.mkdir(paths.USER_FOLDER_PATH)
        print(f'INFORMATION: The local folder AUTOLAB has been created : {paths.USER_FOLDER_PATH}')
    
    # LOCAL CONFIG
    if os.path.exists(paths.DEVICES_INDEX_PATH) is False :
        shutil.copyfile(os.path.join(paths.TEMPLATE_FILES_PATH,'devices_index.ini'),
                        os.path.join(paths.DEVICES_INDEX_PATH))
        print(f'INFORMATION: The configuration file devices_index.ini has been created : {paths.DEVICES_INDEX_PATH}')
        
    # lOCAL CUSTOM DRIVER FOLDER
    if os.path.exists(paths.DRIVERS_PATHS['local']) is False :
        os.mkdir(paths.DRIVERS_PATHS['local'])
