# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:38:15 2019

@author: qchat
"""
import os 
import inspect
import importlib
import autolab
import configparser
from .utilities import emphasize



# =============================================================================
# DRIVERS INSTANTIATION
# =============================================================================

def get_driver_by_config(config_name,**kwargs):
    
    ''' Returns a driver instance using the configuration config_name, overwritted by kwargs '''
    
    config =  dict(get_driver_config(config_name))
    
    assert 'driver' in config.keys(), f"Driver name not found in config '{config_name}'"
    driver_name = config['driver']
    del config['driver']
        
    assert 'connection' in config.keys(), f"Connection type not found in config '{config_name}'"
    connection_type = config['connection']
    del config['connection']

    for key,value in kwargs.items() :
        config[key] = value
    
    instance = get_driver(driver_name,connection_type,**config)
    
    return instance



def get_driver(driver_name, connection_type, **kwargs):
    
    ''' Returns a driver instance '''
    
    assert driver_name in list_drivers(), f'Driver {driver_name} not found'
    driver_lib = load_driver_lib(driver_name)
        
    assert connection_type in get_connection_names(driver_lib),f"Connection type {connection_type} not found for driver {driver_name}"
    instance = get_connection_class(driver_lib,connection_type)(**kwargs)
    
    return instance
    


def load_driver_lib(driver_name):
    
    ''' Returns a driver library (that contains Driver, Driver_XXX, Module_XXX '''
    
    assert driver_name in DRIVERS_INFOS['paths'].keys(), f'Driver {driver_name} not found.'
    driver_dir_path = DRIVERS_INFOS['paths'][driver_name]
    
    # Loading preparation
    driver_path = os.path.join(driver_dir_path,f'{driver_name}.py')

    spec = importlib.util.spec_from_file_location(driver_name, driver_path)
    driver_lib = importlib.util.module_from_spec(spec)
    
    # Save current working directory path
    curr_dir = os.getcwd()
    
    # Go to the driver's directory, in case there are absolute imports
    os.chdir(driver_dir_path)

    # Load the module
    spec.loader.exec_module(driver_lib)
    
    # Come back to previous working directory
    os.chdir(curr_dir)
    
    return driver_lib



# =============================================================================
# DRIVERS LIST HELP
# =============================================================================

def list_drivers():
    
    ''' Returns the list of available drivers '''
    
    return list(DRIVERS_INFOS['paths'].keys())



def show_drivers():
    
    ''' Display the drivers help, that consists in the list of available drivers
    sorted by their categories '''
    
    d = {}
    for driver_name in list_drivers() :
        
        try :
            category = get_driver_category(load_driver_lib(driver_name))
            if category not in d.keys() :
                d[category] = []
            d[category].append(driver_name)
        except :
            pass

    mess = '\n'+emphasize('Available drivers:')+'\n\n'
    for category in sorted(list(d.keys())) :
        mess += f'[{category.upper()}]\n'
        mess += ", ".join([driver for driver in sorted(d[category])])+'\n\n'        
    
    print(mess[:-2])



def driver_help(driver_name):
    
    ''' Display the help of a particular driver (connection types, modules, ...) '''
    
    driver_lib = load_driver_lib(driver_name)
    
    mess = '\n'

    # Name and category if available
    submess = f'Driver "{driver_name}"'
    if hasattr(driver_lib.Driver,'category') : submess += f' ({driver_lib.Driver.category})'
    mess += '='*len(submess)+'\n'+submess+'\n'+'='*len(submess)+'\n\n'

    # Connections types
    mess += 'Available connection(s):\n'
    connections = get_connection_names(driver_lib)
    for connection in connections : 
        mess += f' - {connection}\n'
    mess += '\n'
    
    # Modules
    if hasattr(get_driver_class(driver_lib),'slotNaming') :
        mess += 'Available modules(s):\n'
        modules = get_module_names(driver_lib)
        for module in modules : 
            moduleClass = get_module_class(driver_lib,module)
            mess += f' - {module}'
            if hasattr(moduleClass,'category') : mess += f' ({moduleClass.category})'
            mess += '\n'
        mess += '\n'
    
    mess += f'Configuration example(s) for devices_index.ini:\n\n'
    
    # Arguments of Driver class
    driver_class_args = ''
    defaults_args = get_class_args(get_driver_class(driver_lib))
    for key,value in defaults_args.items() :
        driver_class_args += f'{key} = {value}\n'
    if hasattr(get_driver_class(driver_lib),'slot_naming') :
        driver_class_args += get_driver_class(driver_lib).slot_naming+'\n'
        
    # Arguments of Driver_XXX classes
    for connection in connections :
        
        mess += '[myDeviceName]\n'
        mess += f'driver = {driver_name}\n'
        mess += f'connection = {connection}\n'
        
        # get all optional parameters and default values of __init__ method of Driver_ class
        defaults_args = get_class_args(get_connection_class(driver_lib,connection))
        for key,value in defaults_args.items() :
            mess += f'{key} = {value}\n'

        mess += driver_class_args + '\n'
        
    print(mess)
    
    
    
    
    
    
    
    
    

# =============================================================================
# DRIVERS INSPECTION
# =============================================================================

def get_module_names(driver_lib):
    
    ''' Returns the list of the driver's Module(s) name(s) (classes Module_XXX) '''
    
    return [name.split('_')[1] 
            for name, obj in inspect.getmembers(driver_lib, inspect.isclass) 
            if obj.__module__ is driver_lib.__name__ 
            and name.startswith('Module_')]
    
    
            
def get_connection_names(driver_lib):
    
    ''' Returns the list of the driver's connection types (classes Driver_XXX) '''
    
    return [name.split('_')[1]
            for name, obj in inspect.getmembers(driver_lib, inspect.isclass) 
            if obj.__module__ is driver_lib.__name__ 
            and name.startswith('Driver_')]
    
    
    
def get_driver_category(driver_lib):
    
    ''' Returns the driver's category (from class Driver) '''
    
    driver_class = get_driver_class(driver_lib)
    if hasattr(driver_class,'category'):
        return driver_class.category
    else :
        return 'Other'
    
    
    
def get_driver_class(driver_lib):
    
    ''' Returns the class Driver of the provided driver library '''
    
    assert hasattr(driver_lib,'Driver'), f"Class Driver missing in driver {driver_lib.__name__}"
    assert inspect.isclass(driver_lib.Driver), f"Class Driver missing in driver {driver_lib.__name__}"
    return driver_lib.Driver
    


def get_connection_class(driver_lib,connection):
    
    ''' Returns the class Driver_XXX of the provided driver library and connection type '''
    
    assert connection in get_connection_names(driver_lib)
    return getattr(driver_lib,f'Driver_{connection}')



def get_module_class(driver_lib,module_name):
    
    ''' Returns the class Module_XXX of the provided driver library and module_name'''
    
    assert module_name in get_module_names(driver_lib)
    return getattr(driver_lib,f'Module_{module_name}')



def get_class_args(clas):
    
    ''' Returns the dictionary of the optional arguments required by a class
    with their default values '''
    
    signature = inspect.signature(clas)
    return {k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}







# =============================================================================
# DRIVERS CONFIG
# =============================================================================

def get_driver_config(config_name):
    
    ''' Returns the config associated with config_name '''
    
    assert config_name in list_driver_config(), f"Configuration {config_name} not found"
    return DRIVERS_INFOS['config'][config_name]



def list_driver_config():
    
    ''' Returns the list of available configuration names '''
    
    return list(DRIVERS_INFOS['config'].sections())





# =============================================================================
# DRIVERS INFOS
# =============================================================================


def load_drivers_infos():
    
    ''' Return the current autolab drivers inforamations : 
        - the content of the local_config file  ['config']
        - the paths of the drivers              ['paths']
    '''
    
    paths = autolab.paths
    infos = {}
    
    # Drivers : make a directory of the paths
    driver_dir_paths = []
    for driver_source in paths.DRIVER_SOURCES.values():
        driver_dir_paths += [os.path.join(driver_source,driver_name) 
                            for driver_name in os.listdir(driver_source) 
                            if os.path.isdir(os.path.join(driver_source,driver_name))
                            and f'{driver_name}.py' in os.listdir(os.path.join(driver_source,driver_name))]

    infos['paths'] = {}
    for driver_dir_path in driver_dir_paths : 
        driver_name = os.path.basename(driver_dir_path)
        assert driver_name not in infos['paths'].keys(), f"Each driver must have a unique name. ({driver_name})"
        infos['paths'][driver_name] = driver_dir_path
        

    # Devices : returns the content of the DeviceIndex .ini file
    config = configparser.ConfigParser()
    config.read(paths.LOCAL_CONFIG)
    assert len(set(config.sections())) == len(config.sections()), f"Each device must have a unique name."
    infos['config'] = config
    
    return infos





# Loading the drivers informations at startup
DRIVERS_INFOS = load_drivers_infos()     
        