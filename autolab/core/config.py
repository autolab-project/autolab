# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 14:53:10 2019

@author: qchat
"""

import configparser
from . import paths, stats
import os



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

    # PLOTTER CONFIGURATION FILE
    if os.path.exists(paths.PLOTTER_CONFIG) is False :
        plotter_config = configparser.ConfigParser()
        plotter_config['plugin'] = {'plotter':'plotter'}
        save_config('plotter',plotter_config)
        print(f'The configuration file plotter_config.ini has been created: {paths.PLOTTER_CONFIG}')

def save_config(config_name,config):

    """ This function saves the given config parser in the autolab configuration file """

    with open(getattr(paths,f'{config_name.upper()}_CONFIG'), 'w') as file:
        config.write(file)


def load_config(config_name):

    """ This function loads the autolab configuration file in a config parser """

    config = configparser.ConfigParser()
    config.read(getattr(paths,f'{config_name.upper()}_CONFIG'))
    return config


# def get_attribute(config,section_name,attribute_name):

#     ''' This function get the value of the given parameter of the given header in the provided configparser '''
#     config_section = get_config_section(config,section_name)
#     assert attribute_name in config_section.keys(), f"Attribute '{attribute_name}' not found in section {section_name}."
#     return config_section[attribute_name]

# def get_config_section(config,section_name):

#     ''' Returns section <section_name> from existing <config> object '''

#     assert section_name in config.sections(), f"Section {section_name} not found in configuration file"
#     return config[section_name]


# def load_config_section(config_name,section_name):

#     ''' Returns section <section_name> from configuration file <config_name>_config.ini '''

#     config = load_config(config_name)
#     return get_config_section(config,section_name)


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
            print('This feature has been disabled.')
            autolab_config['stats'] = {'enabled': '0'}
        else :
            print('Thank you !')
            autolab_config['stats'] = {'enabled': '1'}

    # Check server configuration
    if 'server' not in autolab_config.sections() :
        autolab_config['server'] = {'port':4001}
    if 'port' not in autolab_config['server'].keys() :
        autolab_config['server']['port'] = 4001

    # Check control center configuration
    control_center_dict = {'precision': 7,
                           'slider_instantaneous': False,
                           }
    if 'control_center' not in autolab_config.sections() or not set(control_center_dict.keys()).issubset(autolab_config['control_center'].keys()) :
        autolab_config['control_center'] = control_center_dict

    # Check monitor configuration
    monitor_dict = {'precision': 4,
                    }
    if 'monitor' not in autolab_config.sections() or not set(monitor_dict.keys()).issubset(autolab_config['monitor'].keys()) :
        autolab_config['monitor'] = monitor_dict

    # Check scanner configuration
    scanner_dict = {'precision': 15,
                    }
    if 'scanner' not in autolab_config.sections() or not set(scanner_dict.keys()).issubset(autolab_config['scanner'].keys()) :
        autolab_config['scanner'] = scanner_dict

    # # Check plotter configuration
    # plotter_dict = {'precision': 10,
    #                 }
    # if 'plotter' not in autolab_config.sections() or not set(plotter_dict.keys()).issubset(autolab_config['plotter'].keys()) :
    #     autolab_config['plotter'] = plotter_dict


    save_config('autolab',autolab_config)



def get_config(section_name):
    ''' Returns section with section_name from autolab_config.ini '''

    config = load_config('autolab')
    assert section_name in config.sections(), f'Missing {section_name} stats in autolab_config.ini'

    return config[section_name]


def get_stats_config():
    ''' Returns section stats from autolab_config.ini '''

    return get_config('stats')


def get_server_config():
    ''' Returns section server from autolab_config.ini '''

    return get_config('server')


def get_control_center_config():
    ''' Returns section control_center from autolab_config.ini '''

    return get_config('control_center')


def get_monitor_config():
    ''' Returns section monitor from autolab_config.ini '''

    return get_config('monitor')


def get_scanner_config():
    ''' Returns section scanner from autolab_config.ini '''

    return get_config('scanner')


# def get_plotter_config():
#     ''' Returns section plotter from autolab_config.ini '''

#     return get_config('plotter')




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
