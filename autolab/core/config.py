# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 14:53:10 2019

@author: qchat
"""

import configparser
import autolab
import os
import shutil

def check():
    
    """ This function create the default autolab local directory """
        
    # LOCAL DIRECTORY
    if os.path.exists(autolab.paths.USER_FOLDER) is False:
        os.mkdir(autolab.paths.USER_FOLDER)
        print(f'The local directory of AUTOLAB has been created: {autolab.paths.USER_FOLDER}')

    # LOCAL CONFIGURATION FILE
    if os.path.exists(autolab.paths.LOCAL_CONFIG) is False : 
        shutil.copyfile(autolab.paths.LOCAL_CONFIG_TEMPLATE,autolab.paths.LOCAL_CONFIG)
        print(f'The configuration file local_config.ini has been created: {autolab.paths.LOCAL_CONFIG}')
    
    # lOCAL CUSTOM DRIVER FOLDER
    if os.path.exists(autolab.paths.DRIVER_SOURCES['local']) is False :
        os.mkdir(autolab.paths.DRIVER_SOURCES['local'])
        print(f'The local driver directory has been created: {autolab.paths.DRIVER_SOURCES["local"]}')
    
    # AUTOLAB CONFIGURATION FILE
    if os.path.exists(autolab.paths.AUTOLAB_CONFIG) is False :
        save(configparser.ConfigParser())
        print(f'The configuration file autolab_config.ini has been created: {autolab.paths.AUTOLAB_CONFIG}')
    
    config = load()
    
    # stats
    if 'stats' not in config.sections() or 'enabled' not in config['stats'].keys() :
        
        ans = input(f'{autolab._stats.get_explanation()} Do you agree? [default:yes] > ')
        if ans.strip().lower() == 'no' :
            print('This feature has been disabled. You can enable it back with the function autolab.set_stats_enabled(True).')
            config['stats'] = {'enabled': '0'}
        else :
            print('Thank you !')
            config['stats'] = {'enabled': '1'}
    
        save(config)
        
        

def set_value(header,parameter,value):
    
    ''' This function set the value of the given parameter of the given header in the autolab configuration file'''
    
    config = load()
    assert header in config.sections(), f"Header '{header}' not found in the autolab configuration file."
    assert parameter in config[header].keys(), f"Parameter '{parameter}' not found in header {header}."
    config[header][parameter] = str(value)
    save(config)



def get_value(header,parameter):
    
    ''' This function set the value of the given parameter of the given header in the autolab configuration file'''
     
    config = load()
    assert header in config.sections(), f"Header '{header}' not found in the autolab configuration file."
    assert parameter in config[header].keys(), f"Parameter '{parameter}' not found in header {header}."
    return config[header][parameter]
   
    

def save(config):
    
    """ This function saves the given config parser in the autolab configuration file """
    
    with open(autolab.paths.AUTOLAB_CONFIG, 'w') as file:
        config.write(file)
    
    

def load():
    
    """ This function loads the autolab configuration file in a config parser """
        
    config = configparser.ConfigParser()
    config.read(autolab.paths.AUTOLAB_CONFIG)
    
    return config

