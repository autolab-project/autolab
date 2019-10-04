#!/bin/bash
# -*- coding: utf-8 -*-

import os 
import shutil
import configparser
import re

_LIBPATH          = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
_CONFIGPATH       = os.path.dirname(_LIBPATH)

#userFolderPath    = os.path.expanduser('~')
localFolderPath     = os.path.join(_CONFIGPATH,'toniq_local_config')
exampleDevindexPath = os.path.join(_LIBPATH,'More/local_config_example/devices_index.ini')
devindexPath        = os.path.join(localFolderPath,'devices_index.ini')


def save_config(config):
    with open('devices_index.ini','w') as local_config:
        config.write(local_config)

def add_instrument():
    config = getConfig()
    
    section_name = input('Enter a nickname for your instrument:\n')
    config.add_section(section_name)
    
    while True:
        attribute_name = input('\nAttribute (allowed values: driver, address, port, slot[1-9], libpath, param):\n')
        choices = ['driver','address','port','^slot[1-9]$','libpath','param']
        assert [attribute_name for i in choices if re.findall(i,attribute_name)], "attribute not known"
        attribute_value = input(f'Associated value (see {exampleDevindexPath} for examples):\n')
        config[section_name][attribute_name] = attribute_value
        rep = input('Do you want to add other attributes? [y/n] ')
        if rep == 'n': break
            
    print(f'\nInstrument {section_name} with items:')
    for item in config[section_name].items():
        print(item)
    
    rep = input('Do you want to save? [y/n] ')
    if rep == 'y':
        save_config(config)
        print(f'\nInstrument {section_name} successfully added to {devindexPath}')
    else:
        print(f'\n{devindexPath} NOT modified')
        
def remove_instrument():
    config = getConfig()
    
    section_name = input('Instrument to remove:\n')
    assert section_name in config.sections(), f"{section_name} is not an existing instrument"
    
    config.remove_section(section_name)
    
    save_config(config)
    print(f'\nInstrument {section_name} successfully remove from {devindexPath}')
    
def getConfig():
    os.chdir(localFolderPath)
    config = configparser.ConfigParser()
    config.read(devindexPath)
    return config

def makeConfig():
    # LOCAL FOLDER
    if os.path.exists(localFolderPath) is False:
        os.mkdir(localFolderPath)
        print(f'WARNING: toniq_local_folder created : {localFolderPath}')
    # LOCAL FILE (devices_index.ini)
    if os.path.exists(devindexPath) is False:
        shutil.copyfile(exampleDevindexPath,devindexPath)
        print(f'WARNING: Local devices_index.ini duplicated from {exampleDevindexPath} in the local folder.')


def checkConfig():
    makeConfig()
    # CHECK CONFIG
    config = getConfig()

    try :
        txt = 'WARNING devices_index .ini file: '
        assert 'paths' in config.sections(), txt+"Missing section 'paths'."
        assert 'driverspath' in config['paths'], txt+"Missing parameter 'driverspath' in section 'paths."
        assert 'devicesindexpath' in config['paths'], txt+"Missing parameter 'deviceindexpath' in section 'paths'."
        assert os.path.exists(config['paths']['DriversPath']), txt+"Path provided in parameter 'driverspath' is incorrect."
        assert os.path.exists(config['paths']['DevicesIndexPath']), txt+"Path provided in parameter 'devicesindexpath' is incorrect."      
    except Exception as e :
        print(e)
        return False
    
    return True
