# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 16:02:59 2019

@author: qchat
"""
import os 
import shutil
import configparser

_LIBPATH = os.path.dirname(os.path.realpath(__file__))
userFolderPath = os.path.expanduser('~')
localFolderPath = os.path.join(userFolderPath,'usit')
localConfigPath = os.path.join(localFolderPath,'config.ini')
packageConfigPath = os.path.join(_LIBPATH,'config.ini')


def getConfig():
    config = configparser.ConfigParser()
    config.read(localConfigPath)
    return config
    

def checkConfig():

    # LOCAL FOLDER
    if os.path.exists(localFolderPath) is False :
        os.mkdir(localFolderPath)
        print(f'USIT local folder created : {localFolderPath}')
    
    # LOCAL CONFIG
    if os.path.exists(localConfigPath) is False :
        shutil.copyfile(packageConfigPath,localConfigPath)
        print(f'Local config.ini file not found, duplicated from package in the local folder.')
        
    # CHECK CONFIG
    config = getConfig()
    try :
        txt = 'config.ini file: '
        assert 'paths' in config.sections(), txt+"Missing section 'paths'."
        assert 'driverspath' in config['paths'], txt+"Missing parameter 'driverspath' in section 'paths."
        assert 'devicesindexpath' in config['paths'], txt+"Missing parameter 'deviceindexpath' in section 'paths'."
        assert os.path.exists(config['paths']['DriversPath']), txt+"Path provided in parameter 'driverspath' is incorrect."
        assert os.path.exists(config['paths']['DevicesIndexPath']), txt+"Path provided in parameter 'devicesindexpath' is incorrect."      
    except Exception as e :
        print(e)
        return False
    
    return True


