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
from .utilities import emphasize,underline

    
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
    
    ''' Returns a driver library (that contains Driver, Driver_XXX, Module_XXX) '''
    
    driver_dir_path = get_driver_path(driver_name)
        
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
    
    return list(DRIVERS_PATH.keys())



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
    
    
    # Load list of all parameters
    driver_lib = load_driver_lib(driver_name)
    params = {}
    params['driver'] = driver_name
    params['connection'] = {}
    for conn in get_connection_names(driver_lib) : 
        params['connection'][conn] = get_class_args(get_connection_class(driver_lib,conn))
    params['other'] = get_class_args(get_driver_class(driver_lib))
    if hasattr(get_driver_class(driver_lib),'slot_config') :
        params['other']['slot1'] = f'{get_driver_class(driver_lib).slot_config}'
        params['other']['slot1_name'] = 'my_<MODULE_NAME>'
    
    mess = '\n'

    # Name and category if available
    submess = f'Driver "{driver_name}"'
    if hasattr(driver_lib.Driver,'category') : submess += f' ({driver_lib.Driver.category})'
    mess += emphasize(submess,sign='=') + '\n'
    
    # Connections types
    mess += '\nConnections types:\n'
    for connection in params['connection'].keys() : 
        mess += f' - {connection}\n'
    mess += '\n'
    
    # Modules
    if hasattr(get_driver_class(driver_lib),'slot_config') :
        mess += 'Modules:\n'
        modules = get_module_names(driver_lib)
        for module in modules : 
            moduleClass = get_module_class(driver_lib,module)
            mess += f' - {module}'
            if hasattr(moduleClass,'category') : mess += f' ({moduleClass.category})'
            mess += '\n'
        mess += '\n'
   
    # Example of get_driver
    mess += '\n' + underline('Example(s) to instantiate a driver:') + '\n\n'
    for conn in params['connection'].keys() :
        mess += f"\ta = autolab.get_driver('{params['driver']}', '{conn}'"
        for arg,value in params['connection'][conn].items():
            mess += f", {arg}='{value}'"
        for arg,value in params['other'].items():
            mess += f", {arg}='{value}'"
        mess += ')\n'
            
    # Example of set_driver_config
    mess += '\n\n' + underline('Example(s) to save a driver configuration by command-line:') + '\n\n'
    for conn in params['connection'].keys() :
        mess += f"\tautolab.set_driver_config('my_{params['driver']}', driver='{params['driver']}', connection='{conn}'"
        for arg,value in params['connection'][conn].items():
            mess += f", {arg}='{value}'"
        for arg,value in params['other'].items():
            mess += f", {arg}='{value}'"
        mess += ')\n'
            
    # Example of set_driver_config
    mess += '\n\n' + underline('Example(s) to save a driver configuration by editing the file local_config.ini:') + '\n'
    for conn in params['connection'].keys() :
        mess += f"\n\t[my_{params['driver']}]\n"
        mess += f"\tdriver = {params['driver']}\n"
        mess += f"\tconnection = {conn}\n"
        for arg,value in params['connection'][conn].items():
            mess += f"\t{arg} = {value}\n"
        for arg,value in params['other'].items():
            mess += f"\t{arg} = {value}\n"
    
    # Example of get_driver_by_config
    mess += '\n\n' + underline('Example to instantiate a driver with local configuration:') + '\n\n'
    mess += f"\ta = autolab.get_driver_by_config('my_{params['driver']}')"
        
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
# DRIVERS CONFIGS
# =============================================================================
    
def load_driver_configs():
    
    ''' Return the current autolab drivers informations:
        - the content of the local_config file  ['config']
    '''
    
    paths = autolab.paths
    
    config = configparser.ConfigParser()
    config.read(paths.LOCAL_CONFIG)
    assert len(set(config.sections())) == len(config.sections()), f"Each device must have a unique name."
    
    return config



def list_driver_configs():
    
    ''' Returns the list of available configuration names '''
    
    drivers_configs = load_driver_configs()
    return list(drivers_configs.sections())



def get_driver_config(config_name):
    
    ''' Returns the config associated with config_name '''
    
    assert config_name in list_driver_configs(), f"Configuration {config_name} not found"
    drivers_configs = load_driver_configs()
    return drivers_configs[config_name]



def set_driver_config(config_name,modify=False,**kwargs):
    
    ''' Add a new driver config (kwargs) or modify an existing one in the configuration file.
    Set the option modify=True to apply changes in an existing config (for safety) '''
    
    if modify is False :
        assert config_name not in list_driver_configs(), f'Configuration "{config_name}" already exists. Please set the option modify=True to apply changes, or delete the configuration first.'
    
    driver_configs = load_driver_configs()
    
    if config_name not in driver_configs.sections():
        driver_configs.add_section(config_name)
    
    for key,value in kwargs.items() :
        driver_configs.set(config_name, key, str(value))
        
    for key in ['driver', 'connection'] :
        assert key in driver_configs[config_name].keys(), f'Missing parameter "{key}" in the configuration'
    assert driver_configs.get(config_name, 'driver') in list_drivers(), f'Driver "{driver_configs.get(config_name, "driver")}" does not exist'
        
    with open(autolab.paths.LOCAL_CONFIG, 'w') as file:
        driver_configs.write(file)
     


def show_driver_config(config_name):
    
    ''' Display a driver_config as it appears in the configuration file '''
    
    assert config_name in list_driver_configs(), f'Configuration "{config_name}" does not exist.'
    
    driver_configs = load_driver_configs()
    mess = f'\n[{config_name}]\n'
    for key,value in driver_configs[config_name].items() :
        mess += f'{key} = {value}\n'
    print(mess)

        
        
def remove_driver_config(config_name):
    
    ''' Remove a driver_config from the configuration file '''
    
    assert config_name in list_driver_configs(), f'Configuration "{config_name}" does not exist.'
    
    driver_configs = load_driver_configs()
    driver_configs.remove_section(config_name)

    with open(autolab.paths.LOCAL_CONFIG, 'w') as file:
        driver_configs.write(file)



def remove_driver_config_parameter(config_name,param_name):
    
    ''' Remove a parameter of a driver_config in the configuration file '''
    
    assert config_name in list_driver_configs(), f'Configuration "{config_name}" does not exist.'
    
    driver_configs = load_driver_configs()
    assert param_name in driver_configs[config_name].keys(), f'The parameter "{param_name}" does not exist.'
    assert param_name not in ['driver','connection'], f'The parameter "{param_name}" is mandatory.'
    
    driver_configs = load_driver_configs()
    driver_configs.remove_option(config_name,param_name)
    
    with open(autolab.paths.LOCAL_CONFIG, 'w') as file:
        driver_configs.write(file)
    






# =============================================================================
# DRIVERS PATHS
# =============================================================================

def get_driver_path(driver_name):
    
    ''' Returns the config associated with driver_name '''
    
    assert driver_name in DRIVERS_PATH.keys(), f'Driver {driver_name} not found.'
    return DRIVERS_PATH[driver_name]



def list_driver_paths():
    
    ''' Returns the list of available configuration names '''
    
    return list(DRIVERS_PATH.sections())



def load_drivers_paths():
    
    ''' Return the current autolab drivers informations : 
        - the paths of the drivers
    '''
    
    paths = autolab.paths
    
    # Drivers : make a directory of the paths
    driver_dir_paths = []
    for driver_source in paths.DRIVER_SOURCES.values():
        driver_dir_paths += [os.path.join(driver_source,driver_name) 
                            for driver_name in os.listdir(driver_source) 
                            if os.path.isdir(os.path.join(driver_source,driver_name))
                            and f'{driver_name}.py' in os.listdir(os.path.join(driver_source,driver_name))]

    infos = {}
    for driver_dir_path in driver_dir_paths : 
        driver_name = os.path.basename(driver_dir_path)
        assert driver_name not in infos.keys(), f"Each driver must have a unique name. ({driver_name})"
        infos[driver_name] = driver_dir_path
        
    return infos








# Loading the drivers informations at startup
DRIVERS_PATH   = load_drivers_paths()
        
