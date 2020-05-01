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
from . import paths

# =============================================================================
# DRIVERS INSTANTIATION
# =============================================================================

def get_driver(driver_name,connection_type,**kwargs):

    ''' Returns a driver instance using configuration provided in kwargs'''

    # Load Driver module
    assert driver_name in list_drivers(), f"Driver {driver_name} not found in autolab's drivers"
    driver_lib = load_driver_lib(driver_name)

    # Driver instance
    driver_instance = get_connection_class(driver_lib,connection_type)(**kwargs)

    return driver_instance



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

    # To be sure that the list is up to date
    update_drivers_paths()
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

    driver_utilities_path = os.path.join(os.path.dirname(get_driver_path(driver_name)),f'{driver_name}_utilities.py')
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

    assert connection in get_connection_names(driver_lib),f"Invalid connection type {connection} for driver {driver_lib.__name__}"
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
# DRIVERS PATHS
# =============================================================================

def get_driver_path(driver_name):

    ''' Returns the config associated with driver_name '''

    assert driver_name in DRIVERS_PATHS.keys(), f'Driver {driver_name} not found.'
    return DRIVERS_PATHS[driver_name]['path']


def load_drivers_paths():

    ''' Returns a dictionary with :
        - key : name of the driver
        - value : path of the driver python script
    '''

    drivers_paths = {}
    for source_name,source_path in paths.DRIVER_SOURCES.items():
        for driver_name in os.listdir(source_path) :
            temp_path = os.path.join(source_path,driver_name)
            if os.path.isdir(temp_path) and f'{driver_name}.py' in os.listdir(temp_path) :
                assert driver_name not in drivers_paths.keys(), f"Two drivers where found with the name '{driver_name}'. Each driver must have a unique name."
                drivers_paths[driver_name] = {'path':os.path.join(temp_path,f'{driver_name}.py'),
                                              'source':source_name}

    return drivers_paths


def update_drivers_paths():
    global DRIVERS_PATH
    DRIVERS_PATHS = load_drivers_paths()

# Loading the drivers informations at startup
DRIVERS_PATHS = load_drivers_paths()
