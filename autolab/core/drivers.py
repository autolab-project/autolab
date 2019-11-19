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
from .utilities import emphasize,underline,two_columns

    
# =============================================================================
# DRIVERS INSTANTIATION
# =============================================================================

def get_driver(name, **kwargs):
    
    ''' Returns a driver instance '''
    
    if name in list_local_configs() :
        
        # Load config object
        config = dict(get_local_config(name))
        
        # Overwrite config with provided configuration in kwargs
        for key,value in kwargs.items() :
            config[key] = value
        
        # Check if driver provided
        assert 'driver' in config.keys(), f"Driver name not found in driver config '{name}'"
        driver_name = config['driver']
        del config['driver'] # Because config will be pass to the Driver class
            
    else :
        
        # Create config object
        config = kwargs
    
        # The provided name has to be a driver name
        assert name in list_drivers(), f'Driver {name} not found'
        driver_name = name
        
    # And the argument connection has to be provided
    assert 'connection' in config.keys(), f"Missing connection type for driver '{driver_name}'"
    connection = config['connection']
    del config['connection'] # Because config will be pass to the Driver class
        
    # Load driver library
    driver_lib = load_driver_lib(driver_name)
        
    # Check connection type
    assert connection in get_connection_names(driver_lib),f"Connection type {connection} not found for driver {driver_name}"
    instance = get_connection_class(driver_lib,connection)(**config)
    
    return instance
    


def load_driver_lib(driver_name):
    
    ''' Returns a driver library (that contains Driver, Driver_XXX, Module_XXX) '''
            
    # Loading preparation
    driver_path = get_driver_path(driver_name)
    
    # Laod library
    driver_lib = load_lib(driver_path)
    
    return driver_lib




def load_lib(lib_path):
    
    ''' Return an instance of the python script located at lib_path '''
    
    lib_name = os.path.basename(lib_path).split('.')[0]
    
    # Save current working directory path
    curr_dir = os.getcwd()
    
    # Go to the driver's directory (in case it contains absolute imports)
    os.chdir(os.path.dirname(lib_path))

    # Load the module
    spec = importlib.util.spec_from_file_location(lib_name, lib_path)
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    
    # Come back to previous working directory
    os.chdir(curr_dir)
    
    return lib
    
    
    
    
def load_driver_utilities_lib(driver_utilities_name):
    
    ''' Returns a driver library (that contains Driver, Driver_XXX, Module_XXX) '''
            
    # Loading preparation
    driver_path = get_driver_path(driver_utilities_name.replace('_utilities',''))
    
    # Laod library
    driver_lib = load_utilities_lib(driver_path)
    
    return driver_lib




def load_utilities_lib(lib_path):
    
    ''' Return an instance of the python script located at lib_path '''
    
    lib_name = os.path.basename(lib_path).split('.')[0]
    
    # Save current working directory path
    curr_dir = os.getcwd()
    
    # Go to the driver's directory (in case it contains absolute imports)
    os.chdir(os.path.dirname(lib_path))

    # Load the module
    lib_name = lib_name + '_utilities'
    spec = importlib.util.spec_from_file_location(lib_name, os.path.join(os.path.dirname(lib_path),f'{lib_name}.py'))
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    
    # Come back to previous working directory
    os.chdir(curr_dir)
    
    return lib

# =============================================================================
# DRIVERS LIST HELP
# =============================================================================

def list_drivers():
    
    ''' Returns the list of available drivers '''
    
    return sorted(list(DRIVERS_PATHS.keys()))


    
    
    
    
    

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
    
    
    
def get_driver_category(driver_name):
    
    ''' Returns the driver's category (from class Driver) '''
    
    driver_utilities_path = os.path.join(os.path.dirname(DRIVERS_PATHS[driver_name]),f'{driver_name}_utilities.py')
    category = 'Other'
    if os.path.exists(driver_utilities_path) :
        driver_utilities = load_lib(driver_utilities_path)
        if hasattr(driver_utilities,'category') :
            category = driver_utilities.category
    
    return category
    
    
    
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


def explore_driver(instance,_print=True):
    
    ''' Displays the list of the methods available in this instance '''
    
    methods = get_instance_methods(instance)
    s = 'This instance contains the following functions:\n'
    for method in methods :
        s += f' - {method[0]}({",".join(method[1])})\n'
        
    if _print is True : print(s)
    else : return s


def get_instance_methods(instance):
    
    ''' Returns the list of all the methods (and their args) in that class '''
    
    methods = []
    
    # LEVEL 1
    for name,obj in inspect.getmembers(instance,inspect.ismethod) :
        if name != '__init__' :
            attr = getattr(instance,name)
            args = list(inspect.signature(attr).parameters.keys())
            methods.append([name,args])
            
    # LEVEL 2
    instance_vars = vars(instance)
    for key in instance_vars.keys():
        try :    # explicit to avoid visa and inspect.getmembers issue
            for name,obj in inspect.getmembers(instance_vars[key],inspect.ismethod):
                if inspect.getmembers(instance_vars[key],inspect.ismethod) != '__init__' and inspect.getmembers(instance_vars[key],inspect.ismethod) and name!='__init__':
                    attr = getattr(getattr(instance,key),name)
                    args = list(inspect.signature(attr).parameters.keys())
                    methods.append([f'{key}.{name}',args])
        except : pass
        
    return methods


def get_class_args(clas):
    
    ''' Returns the dictionary of the optional arguments required by a class
    with their default values '''
    
    signature = inspect.signature(clas)
    return {k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}




# =============================================================================
# LOCAL CONFIGS
# =============================================================================
    
def load_local_configs():
    
    ''' Return the current autolab drivers informations:
        - the content of the local_config file  ['config']
    '''
    
    paths = autolab.paths
    
    config = configparser.ConfigParser()
    config.read(paths.LOCAL_CONFIG)
    assert len(set(config.sections())) == len(config.sections()), f"Each device must have a unique name."
    
    return config



def list_local_configs():
    
    ''' Returns the list of available configuration names '''
    
    local_configs = load_local_configs()
    return sorted(list(local_configs.sections()))



def get_local_config(config_name):
    
    ''' Returns the config associated with config_name '''
    
    assert config_name in list_local_configs(), f"Configuration {config_name} not found"
    local_configs = load_local_configs()
    return local_configs[config_name]



def set_local_config(config_name,modify=False,**kwargs):
    
    ''' Add a new driver config (kwargs) or modify an existing one in the configuration file.
    Set the option modify=True to apply changes in an existing config (for safety) '''
    
    if modify is False :
        assert config_name not in list_local_configs(), f'Configuration "{config_name}" already exists. Please set the option modify=True to apply changes, or delete the configuration first.'
    
    local_configs = load_local_configs()
    
    if config_name not in local_configs.sections():
        local_configs.add_section(config_name)
    
    for key,value in kwargs.items() :
        local_configs.set(config_name, key, str(value))
        
    for key in ['driver', 'connection'] :
        assert key in local_configs[config_name].keys(), f'Missing parameter "{key}" in the configuration'
    assert local_configs.get(config_name, 'driver') in list_drivers(), f'Driver "{local_configs.get(config_name, "driver")}" does not exist'
        
    with open(autolab.paths.LOCAL_CONFIG, 'w') as file:
        local_configs.write(file)
     


def show_local_config(config_name,_print=True):
    
    ''' Display a local_config as it appears in the configuration file '''
    
    assert config_name in list_local_configs(), f'Configuration "{config_name}" does not exist.'
    
    local_configs = load_local_configs()
    mess = f'\n[{config_name}]\n'
    for key,value in local_configs[config_name].items() :
        mess += f'{key} = {value}\n'
    
    if _print is True : print(mess)
    else : return mess

        
        
def remove_local_config(config_name):
    
    ''' Remove a local_config from the configuration file '''
    
    assert config_name in list_local_configs(), f'Configuration "{config_name}" does not exist.'
    
    local_configs = load_local_configs()
    local_configs.remove_section(config_name)

    with open(autolab.paths.LOCAL_CONFIG, 'w') as file:
        local_configs.write(file)



def remove_local_config_parameter(config_name,param_name):
    
    ''' Remove a parameter of a local_config in the configuration file '''
    
    assert config_name in list_local_configs(), f'Configuration "{config_name}" does not exist.'
    
    local_configs = load_local_configs()
    assert param_name in local_configs[config_name].keys(), f'The parameter "{param_name}" does not exist.'
    assert param_name not in ['driver','connection'], f'The parameter "{param_name}" is mandatory.'
    
    local_configs = load_local_configs()
    local_configs.remove_option(config_name,param_name)
    
    with open(autolab.paths.LOCAL_CONFIG, 'w') as file:
        local_configs.write(file)
    

def config_help(driver_name, _print=True, _parser=False):
    
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
    submess = f'Driver "{driver_name}" ({get_driver_category(driver_name)})'
    mess += emphasize(submess,sign='=') + '\n'
    
    # Connections types
    c_option=''
    if _parser: c_option='(-C option)'
    mess += f'\nAvailable connections types {c_option}:\n'
    for connection in params['connection'].keys() : 
        mess += f' - {connection}\n'
    mess += '\n'
    
    # Modules
    if hasattr(get_driver_class(driver_lib),'slot_config') :
        mess += 'Available modules:\n'
        modules = get_module_names(driver_lib)
        for module in modules : 
            moduleClass = get_module_class(driver_lib,module)
            mess += f' - {module}'
            if hasattr(moduleClass,'category') : mess += f' ({moduleClass.category})'
            mess += '\n'
        mess += '\n'
   
    # Example of get_driver
    mess += '\n' + underline('Example(s) to load a Driver or a Device:') + '\n\n'
    for conn in params['connection'].keys() :
        if _parser is False :
            args_str = f"'{params['driver']}', connection='{conn}'"
            for arg,value in params['connection'][conn].items():
                args_str += f", {arg}='{value}'"
            for arg,value in params['other'].items():
                args_str += f", {arg}='{value}'"
            mess += f"   a = autolab.get_driver({args_str})\n"
            mess += f"   a = autolab.get_device({args_str})\n"
        else : 
            args_str = f"-D {params['driver']} -C {conn} "
            for arg,value in params['connection'][conn].items():
                if arg == 'address' : args_str += f"-A {value} "
                if arg == 'port' : args_str += f"-P {value} "
            if len(params['other'])>0 : args_str += '-O '
            for arg,value in params['other'].items():
                args_str += f"{arg}={value} "
            mess += f"   autolab driver {args_str} \n"
            mess += f"   autolab device {args_str} \n"
            
    # Example of set_local_config
    mess += '\n\n' + underline('Example(s) to save a configuration by command-line:') + '\n\n'
    for conn in params['connection'].keys() :
        if _parser is False :
            args_str = f"'my_{params['driver']}', driver='{params['driver']}', connection='{conn}'"
            for arg,value in params['connection'][conn].items():
                args_str += f", {arg}='{value}'"
            for arg,value in params['other'].items():
                args_str += f", {arg}='{value}'"
            mess += f"   autolab.set_local_config({args_str})\n"
        else : 
            mess += '   Available soon through OS shell\n'
            
    # Example of set_local_config
    mess += '\n\n' + underline('Example(s) to save a configuration by editing the file local_config.ini:') + '\n'
    for conn in params['connection'].keys() :
        mess += f"\n   [my_{params['driver']}]\n"
        mess += f"   driver = {params['driver']}\n"
        mess += f"   connection = {conn}\n"
        for arg,value in params['connection'][conn].items():
            mess += f"   {arg} = {value}\n"
        for arg,value in params['other'].items():
            mess += f"   {arg} = {value}\n"
    
    # Example of get_driver_by_config
    mess += '\n\n' + underline('Example to instantiate a Driver or a Device with a local configuration:') + '\n\n'
    if _parser is False :
        mess += f"   a = autolab.get_driver('my_{params['driver']}')\n"
        mess += f"   a = autolab.get_device('my_{params['driver']}')"
    else :
        mess += f"   autolab driver -D my_{params['driver']}\n"
        mess += f"   autolab device -D my_{params['driver']}\n"
        
    if _print is True : print(mess)
    else : return mess
    




# =============================================================================
# DRIVERS PATHS
# =============================================================================

def get_driver_path(driver_name):
    
    ''' Returns the config associated with driver_name '''
    
    assert driver_name in DRIVERS_PATHS.keys(), f'Driver {driver_name} not found.'
    return DRIVERS_PATHS[driver_name]

def load_drivers_paths():
    
    ''' Returns a dictionary with :
        - key : name of the driver
        - value : path of the driver python script
    '''
    
    paths = autolab.paths
    
    drivers_paths = {}
    for driver_source in paths.DRIVER_SOURCES.values():
        for name in os.listdir(driver_source) :
            temp_path = os.path.join(driver_source,name)
            if os.path.isdir(temp_path) and f'{name}.py' in os.listdir(temp_path) :
                assert name not in drivers_paths.keys(), f"Two drivers where found with the name '{name}'. Each driver must have a unique name."
                drivers_paths[name] = os.path.join(temp_path,f'{name}.py')
              
    return drivers_paths






# =============================================================================
# INFOS
# =============================================================================

def infos(_print=True):
    
    # Gather drivers informations
    drivers = {}
    for driver_name in DRIVERS_PATHS.keys() :
        driver_source = os.path.dirname(os.path.dirname(DRIVERS_PATHS[driver_name]))
        if driver_source not in drivers.keys() : drivers[driver_source] = []
        drivers[driver_source].append(driver_name)
    
    # Gather local config informations
    local_configs = list_local_configs()
    
    # Print infos
    s = '\n'
    s += f'{len(DRIVERS_PATHS)} drivers found\n'
    s += f'{len(local_configs)} local configurations found\n\n'
    for driver_source in drivers.keys() : 
        s += f'Drivers in {driver_source}:\n'
        txt_list = [[f'    - {driver_name}',f'({get_driver_category(driver_name)})']
                    for driver_name in drivers[driver_source] ]
        s += two_columns(txt_list)+'\n\n'
        
    s += 'Local configurations:\n'
    txt_list = [[f'    - {config_name}',f'({get_local_config(config_name)["driver"]})']
                for config_name in local_configs ]
    s += two_columns(txt_list)+'\n'
    
    if _print is True : print(s)
    else : return s
    
    


# Loading the drivers informations at startup
DRIVERS_PATHS = load_drivers_paths()
        
