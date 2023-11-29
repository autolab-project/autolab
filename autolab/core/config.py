# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 14:53:10 2019

@author: qchat
"""

import configparser
from . import paths
import os



# ==============================================================================
# GENERAL
# ==============================================================================

def initialize_local_directory():

    """ This function creates the default autolab local directory """

    # LOCAL DIRECTORY
    if not os.path.exists(paths.USER_FOLDER):
        os.mkdir(paths.USER_FOLDER)
        print(f'The local directory of AUTOLAB has been created: {paths.USER_FOLDER}')

    # DEVICES CONFIGURATION FILE
    if not os.path.exists(paths.DEVICES_CONFIG):
        devices_config = configparser.ConfigParser()
        devices_config['system'] = {'driver':'system','connection':'DEFAULT'}
        save_config('devices',devices_config)
        print(f'The devices configuration file devices_config.ini has been created: {paths.DEVICES_CONFIG}')

    # DRIVER FOLDERS
    if not os.path.exists(paths.DRIVERS):
        os.mkdir(paths.DRIVERS)
        print(f"The drivers directory has been created: {paths.DRIVERS}")
    if not os.path.exists(paths.DRIVER_SOURCES['official']):
        os.mkdir(paths.DRIVER_SOURCES['official'])
        print(f'The official driver directory has been created: {paths.DRIVER_SOURCES["official"]}')
    if not os.path.exists(paths.DRIVER_SOURCES['local']):
        os.mkdir(paths.DRIVER_SOURCES['local'])
        print(f'The local driver directory has been created: {paths.DRIVER_SOURCES["local"]}')

    # AUTOLAB CONFIGURATION FILE
    if not os.path.exists(paths.AUTOLAB_CONFIG):
        save_config('autolab',configparser.ConfigParser())
        print(f'The configuration file autolab_config.ini has been created: {paths.AUTOLAB_CONFIG}')

    # PLOTTER CONFIGURATION FILE
    if not os.path.exists(paths.PLOTTER_CONFIG):
        save_config('plotter',configparser.ConfigParser())
        print(f'The configuration file plotter_config.ini has been created: {paths.PLOTTER_CONFIG}')

def save_config(config_name,config):

    """ This function saves the given config parser in the autolab configuration file """

    with open(getattr(paths,f'{config_name.upper()}_CONFIG'), 'w') as file:
        config.write(file)


def load_config(config_name):

    """ This function loads the autolab configuration file in a config parser """

    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
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

    # Check server configuration
    server_dict = {'port': 4001,
                   }
    if 'server' in autolab_config.sections() :
        if 'port' in autolab_config['server'].keys() :
            server_dict['port'] = autolab_config['server']['port']
    autolab_config['server'] = server_dict

    # Check GUI configuration
    GUI_dict = {'QT_API': "default",
                }
    if 'GUI' in autolab_config.sections() :
        if 'QT_API' in autolab_config['GUI'].keys() :
            GUI_dict['QT_API'] = autolab_config['GUI']['QT_API']
    autolab_config['GUI'] = GUI_dict
    autolab_config.set('GUI', '# QT_API -> Choose between default, pyqt5, pyside2, pyqt6 and pyside6')

    # Check control center configuration
    control_center_dict = {'precision': 7,
                           'print': True,
                           'logger': False,
                           }
    if 'control_center' in autolab_config.sections():
        if 'precision' in autolab_config['control_center'].keys() :
            control_center_dict['precision'] = autolab_config['control_center']['precision']
        if 'print' in autolab_config['control_center'].keys() :
            control_center_dict['print'] = autolab_config['control_center']['print']
        if 'logger' in autolab_config['control_center'].keys() :
            control_center_dict['logger'] = autolab_config['control_center']['logger']
    autolab_config['control_center'] = control_center_dict

    # Check monitor configuration
    monitor_dict = {'precision': 4,
                    'save_figure': True,
                    }
    if 'monitor' in autolab_config.sections():
        if 'precision' in autolab_config['monitor'].keys() :
            monitor_dict['precision'] = autolab_config['monitor']['precision']
        if 'save_figure' in autolab_config['monitor'].keys() :
            monitor_dict['save_figure'] = autolab_config['monitor']['save_figure']
    autolab_config['monitor'] = monitor_dict

    # Check scanner configuration
    scanner_dict = {'precision': 15,
                    'recipe_size': [0, 500, 0],
                    'save_config': True,
                    'save_figure': True,
                    }
    if 'scanner' in autolab_config.sections():
        if 'precision' in autolab_config['scanner'].keys() :
            scanner_dict['precision'] = autolab_config['scanner']['precision']
        if 'recipe_size' in autolab_config['scanner'].keys() :
            scanner_dict['recipe_size'] = autolab_config['scanner']['recipe_size']
        if 'save_config' in autolab_config['scanner'].keys() :
            scanner_dict['save_config'] = autolab_config['scanner']['save_config']
        if 'save_figure' in autolab_config['scanner'].keys() :
            scanner_dict['save_figure'] = autolab_config['scanner']['save_figure']
    autolab_config['scanner'] = scanner_dict

    # # Check plotter configuration
    # plotter_dict = {'precision': 10,
    #                 }
    # if 'plotter' in autolab_config.sections():
    #     if 'precision' in autolab_config['plotter'].keys() :
    #         plotter_dict['precision'] = autolab_config['plotter']['precision']
    # autolab_config['plotter'] = plotter_dict

    save_config('autolab',autolab_config)


def get_config(section_name):
    ''' Returns section with section_name from autolab_config.ini '''

    config = load_config('autolab')
    assert section_name in config.sections(), f'Missing {section_name} stats in autolab_config.ini'

    return config[section_name]


def get_server_config():
    ''' Returns section server from autolab_config.ini '''

    return get_config('server')


def get_GUI_config():
    ''' Returns section QT_API from autolab_config.ini '''

    return get_config('GUI')

def get_control_center_config():
    ''' Returns section control_center from autolab_config.ini '''

    return get_config('control_center')


def get_monitor_config():
    ''' Returns section monitor from autolab_config.ini '''

    return get_config('monitor')


def get_scanner_config():
    ''' Returns section scanner from autolab_config.ini '''

    return get_config('scanner')


# ==============================================================================
# PLOTTER CONFIG
# ==============================================================================

def check_plotter_config():

    """ This function checks config file structures """

    plotter_config = load_config('plotter')

    # Check plugin configuration
    plugin_dict = {'plotter': 'plotter'}
    if 'plugin' in plotter_config.sections():
        plugin_dict = dict()
        for plugin_name in plotter_config['plugin'].keys():
            plugin_dict[plugin_name] = plotter_config['plugin'][plugin_name]
    plotter_config['plugin'] = plugin_dict

    # Check device configuration
    device_dict = {'address': 'dummy.array_1D'}
    if 'device' in plotter_config.sections():
        if 'address' in plotter_config['device'].keys():
            device_dict['address'] = plotter_config['device']['address']

    plotter_config['device'] = device_dict

    save_config('plotter',plotter_config)





# =============================================================================
# DEVICES CONFIG
# =============================================================================

def get_all_devices_configs():

    ''' Returns current devices configuration '''

    config = load_config('devices')
    assert len(set(config.sections())) == len(config.sections()), "Each device must have a unique name."

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
