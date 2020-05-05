# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 14:53:10 2019

@author: qchat
"""

import configparser
from . import paths, stats
import os
import shutil



# ==============================================================================
# GENERAL
# ==============================================================================

def initialize_local_directory():

    """ This function creates the default autolab local directory """

    # LOCAL DIRECTORY
    if os.path.exists(paths.USER_FOLDER) is False:
        os.mkdir(paths.USER_FOLDER)
        print(f'The local directory of AUTOLAB has been created: {paths.USER_FOLDER}')

    # DEVICES CONFIGURATION FILE
    if os.path.exists(paths.DEVICES_CONFIG) is False :
        devices_config = configparser.ConfigParser()
        devices_config['system'] = {'driver':'system','connection':'DEFAULT'}
        save_config('devices',devices_config)
        print(f'The devices configuration file devices_config.ini has been created: {paths.DEVICES_CONFIG}')

    # lOCAL CUSTOM DRIVER FOLDER
    if os.path.exists(paths.DRIVER_SOURCES['local']) is False :
        os.mkdir(paths.DRIVER_SOURCES['local'])
        print(f'The local driver directory has been created: {paths.DRIVER_SOURCES["local"]}')

    # AUTOLAB CONFIGURATION FILE
    if os.path.exists(paths.AUTOLAB_CONFIG) is False :
        save_config('autolab',configparser.ConfigParser())
        print(f'The configuration file autolab_config.ini has been created: {paths.AUTOLAB_CONFIG}')


def save_config(config_name,config):

    """ This function saves the given config parser in the autolab configuration file """

    with open(getattr(paths,f'{config_name.upper()}_CONFIG'), 'w') as file:
        config.write(file)


def load_config(config_name):

    """ This function loads the autolab configuration file in a config parser """

    config = configparser.ConfigParser()
    config.read(getattr(paths,f'{config_name.upper()}_CONFIG'))
    return config


#def get_attribute(name,config,header,attribute):

#    ''' This function get the value of the given parameter of the given header in the provided configparser '''

#    assert header in config.sections(), f"Header '{header}' not found in the configuration file."
#    assert parameter in config[header].keys(), f"Parameter '{parameter}' not found in header {header}."
#    return config[header][parameter]

#def get_config_section(config,section_name):

#    ''' Returns section <section_name> from existing <config> object '''

#    assert section_name in config.sections(), f"Section {section_name} not found in configuration file"
#    return config[section_name]


#def load_config_section(config_name,section_name):

#    ''' Returns section <section_name> from configuration file <config_name>_config.ini '''

#    config = load_config(config_name)
#    return get_config_section(config,section_name)


# ==============================================================================
# AUTOLAB CONFIG
# ==============================================================================

def check_autolab_config():

    """ This function checks config file structures """

    autolab_config = load_config('autolab')

    # Check stats configuration
    if 'stats' not in autolab_config.sections() or 'enabled' not in autolab_config['stats'].keys() :

        ans = input(f'{stats.startup_text} Do you agree? [default:yes] > ')
        if ans.strip().lower() == 'no' :
            print('This feature has been disabled. You can enable it back with the function autolab.set_stats_enabled(True).')
            autolab_config['stats'] = {'enabled': '0'}
        else :
            print('Thank you !')
            autolab_config['stats'] = {'enabled': '1'}


    # Check server configuration
    if 'server' not in autolab_config.sections() :
        autolab_config['server'] = {'local_ip':'192.168.1.241','port':4001}
    if 'local_ip' not in autolab_config['server'].keys() :
        autolab_config['server']['local_ip'] = '192.168.1.241'
    if 'port' not in autolab_config['server'].keys() :
        autolab_config['server']['port'] = 4001


    save_config('autolab',autolab_config)


def get_stats_config():

    ''' Returns section stats from autolab_config.ini '''

    config = load_config('autolab')
    assert 'stats' in config.sections(), 'Missing section stats in autolab_config.ini'

    return config['stats']


def get_server_config():

    ''' Returns section server from autolab_config.ini '''

    config = load_config('autolab')
    assert 'server' in config.sections(), 'Missing section server in autolab_config.ini'

    return config['server']



# =============================================================================
# DEVICES CONFIG
# =============================================================================

def get_all_devices_configs():

    ''' Returns current devices configuration '''

    config = load_config('devices')
    assert len(set(config.sections())) == len(config.sections()), f"Each device must have a unique name."

    return config



def list_all_devices_configs():

    ''' Returns the list of available configuration names '''

    devices_configs = get_all_devices_configs()
    return sorted(list(devices_configs.sections()))



def get_device_config(config_name):

    ''' Returns the config associated with config_name '''

    assert config_name in list_all_devices_configs(), f"Device configuration {config_name} not found"
    devices_configs = get_all_devices_configs()
    return devices_configs[config_name]
