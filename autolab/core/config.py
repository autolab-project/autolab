# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 15:17:16 2020

@author: qchat
"""

import configparser
from . import paths, telemetry
import os


# ==============================================================================
# GENERAL
# ==============================================================================

def check_local_directory():

    """ This function creates the default autolab local directory in the user home"""

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



# ==============================================================================
# AUTOLAB CONFIG
# ==============================================================================

def check_autolab_config():

    """ This function checks config file structures """

    autolab_config = load_config('autolab')

    # Check stats configuration
    if 'telemetry' not in autolab_config.sections() or 'enabled' not in autolab_config['telemetry'].keys() :
        
        change_text = 'To change it, edit the autolab_config.ini file.'
        ans = input(f'{telemetry.init_text}\nDo you agree? [default:yes] > ')
        if ans.strip().lower() == 'no' :
            autolab_config['telemetry'] = {'enabled': '0'}
            print(f'\nTelemetry has been disabled. {change_text}')
        else :
            autolab_config['telemetry'] = {'enabled': '1'}
            print(f'\nThank you! {change_text}')

    # Check server configuration
    if 'server' not in autolab_config.sections() :
        autolab_config['server'] = {'port':4001}
    if 'port' not in autolab_config['server'].keys() :
        autolab_config['server']['port'] = 4001

    save_config('autolab',autolab_config)


def get_stats_config():

    ''' Returns section stats from autolab_config.ini '''

    config = load_config('autolab')
    assert 'telemetry' in config.sections(), 'Missing section telemetry in autolab_config.ini'

    return config['stats']


def get_server_config():

    ''' Returns section server from autolab_config.ini '''

    config = load_config('autolab')
    assert 'server' in config.sections(), 'Missing section server in autolab_config.ini'

    return config['server']

