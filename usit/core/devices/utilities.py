# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 10:02:22 2019

@author: qchat
"""

import os
import importlib
import inspect
import configparser
import usit
    
    
    
def getLibrary(driver_path):
    
    """ Open the library located at the path provided """
    
    driverDir = os.path.dirname(driver_path)
    scriptName = os.path.splitext(os.path.basename(driver_path))[0]
    
    spec = importlib.util.spec_from_file_location(scriptName, driver_path)
    lib = importlib.util.module_from_spec(spec)
    
    currDir = os.getcwd()
    os.chdir(driverDir)
    
    try : 
        spec.loader.exec_module(lib)
    except :
        print(f'Impossible to load {driver_path}')
        
    os.chdir(currDir)
    
    return lib
    


def getDeviceObjects(deviceName):
    
    """ Return the class 'Device' instantiated with the provided address, 
    and the function 'configure' of the driver """
    
    # Check if device name exists in device index
    assert deviceName in list_devices(), f"Device {deviceName} not found in the index"
    index = DEVICES_INDEX[deviceName]
    
    # Check if driver exists
    driverName = index['driver']
    assert driverName in usit.drivers.list(), f"Driver {driverName} not found"   
    driver = getattr(usit.drivers,driverName)
    
    # Check if Device class exists in the driver
    className = 'Device'
    if 'class' in index.keys() :
        className = index['class']
    assert hasattr(driver,className), f"There is no class {className} in the driver script"
    driverClass = getattr(driver,className)
    assert inspect.isclass(driverClass), f"The object {className} is not a class in the driver script"

    # Check if usit_config.py exists
    configPath = os.path.join(usit._DRIVERS_PATH,driverName,'usit_config.py')
    assert os.path.exists(configPath), f"Missing usit_config.py file"
    
    # Laod usit_config
    configLib = getLibrary(configPath)
    
    # Check if "configure" function exists inside
    assert hasattr(configLib,'configure'), "There is no function 'configure' in the script usit_config.py"
    configFunc = getattr(configLib,'configure')
    assert inspect.isfunction(configFunc), "The object 'configure' is not a function in the script usit_config.py"
    
    # kwargs creation
    kwargs = dict(index)
    del kwargs['driver']
    if 'class' in kwargs.keys() : del kwargs['class']
    instance = driverClass(**kwargs)
    
    return instance, configFunc
    





# =============================================================================
#                   DEVICES INDEX
# =============================================================================

def check_driver(name):
    
    """ Test if the provided name corresponds to a correct driver folder """
    
    try : 
        
        # Device itself
        assert name in usit.drivers.list()

        # Usit config file
        config_path = os.path.join(usit._DRIVERS_PATH,name,'usit_config.py')
        assert os.path.exists(config_path)

        return True
    
    except :
        return False
    

def loadDevicesIndex():
    
    """ Return the content of the DeviceIndex .ini file content in a pandas dataframe """
    
    filePath = os.path.join(usit._USER_FOLDER_PATH,'devices_index.ini')
    
    index = configparser.ConfigParser()
    index.read(filePath)
    
    # Est ce tous les noms de devices sont uniques ?
    namelist = index.sections()
    assert len(set(namelist)) == len(namelist), "Device index loading: 2 devices cannot have the same name."
    
    for name in index.sections() :
        # Est ce qu'un nom de driver est bien fourni ?
        assert 'driver' in index[name].keys(), f"Device index loading: Device '{name}' has no driver provided"
        
    return index


def list_devices():
    return list(DEVICES_INDEX.sections())


DEVICES_INDEX = loadDevicesIndex()
    

    