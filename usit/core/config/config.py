# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 16:02:59 2019

@author: qchat
"""
import os 
import shutil
import usit

def checkConfig():

    # LOCAL FOLDER
    localFolderPath = usit._USER_FOLDER_PATH
    if os.path.exists(localFolderPath) is False :
        os.mkdir(localFolderPath)
        print(f'INFORMATION: The local folder USIT has been created : {localFolderPath}')
    
    # LOCAL CONFIG
    localConfigPath = os.path.join(localFolderPath,'devices_index.ini')
    if os.path.exists(localConfigPath) is False :
        packageConfigPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),'devices_index_template.ini')
        shutil.copyfile(packageConfigPath,localConfigPath)
        print(f'INFORMATION: The configuration file devices_index.ini has been created : {localConfigPath}')
        


