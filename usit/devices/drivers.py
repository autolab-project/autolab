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
import sys

def getDevicesIndex(filePath):
    
    """ Return the content of the DeviceIndex .ini file content in a pandas dataframe """
    
    index = configparser.ConfigParser()
    index.read(filePath)
    assert len(index.sections()) > 0 ,"DeviceIndex .ini file: There is no devices inside."
    namelist = index.sections()
    assert len(set(namelist)) == len(namelist), "DeviceIndex .ini file: 2 devices cannot have the same name."
    
    for name in index.sections() :
        assert 'driver' in index[name].keys(), f"DeviceIndex .ini file: Device '{name}' has no driver provided"
        assert driverExists(index[name]['driver']), f"DeviceIndex .ini file: Driver of device '{name}' is unusable, check the structure"
        
    return index


def driverExists(driver_name) :
    
    """ Test if the provided name corresponds to a correct driver folder """
    
    try : 
        
        # Is a folder with that name present in the drivers folder ?
        path = os.path.join(DRIVERS_PATH,driver_name)
        assert os.path.isdir(path), "Not a folder"
        
        # Does it contains at least 2 python script : 
        # - the driver itself with the same name as the folder
        # - the configuration script usit_config.py
        basename = os.path.basename(path)
        for fileName in [basename + ".py","usit_config.py"] : assert fileName in os.listdir(path), f"No {fileName} file"
    
        return True
    
    except :
        return False
    
    
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
    
def getDeviceClass(driver_name):
    
    """ Returns the class Device (not instantiated) located in the driver script """
    
    path = os.path.join(DRIVERS_PATH,driver_name,driver_name+".py")
    assert os.path.exists(path), f"This is not a correct device folder (no file {driver_name}.py)"
    lib = getLibrary(path)
    assert hasattr(lib,'Device'), "There is no class 'Device' in the driver script"
    assert inspect.isclass(lib.Device), "The object 'Device' is not a class in the driver script"
    return lib.Device
    
def getConfigFunc(driver_name):
    
    """ Returns the function 'configure' located in the script usit_config.py in the driver folder """
    
    path = os.path.join(DRIVERS_PATH,driver_name,'usit_config.py')
    assert os.path.exists(path), "This is not a correct device folder (no file usit_config.py)"
    lib = getLibrary(path)
    assert hasattr(lib,'configure'), "There is no function 'configure' in the script usit_config.py"
    assert inspect.isfunction(lib.configure), "The object 'configure' is not a function in the script usit_config.py"
    return lib.configure

def getDeviceMaterial(deviceName):
    
    """ Return the class 'Device' instantiated with the provided address, 
    and the function 'configure' of the driver """
    
    assert deviceName in get_devices(), f"Device {deviceName} not existing in the index"
    driverName = DEVICES_INDEX[deviceName]['driver']
    kwargs = dict(DEVICES_INDEX[deviceName])
    del kwargs['driver']
    instance = getDeviceClass(driverName)(**kwargs)
    
    return instance, getConfigFunc(driverName)
    


def get_devices():
    return list(DEVICES_INDEX.sections())


config = usit._config
DRIVERS_PATH = config['paths']['DriversPath']
DEVICES_INDEX = getDevicesIndex(config['paths']['DevicesIndexPath'])
    
    
    
    