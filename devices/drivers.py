# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 10:02:22 2019

@author: qchat
"""

import os
import importlib
import inspect
import pandas as pd

def getLocalConfigPath():
    
    """ Returns the path of the 'local_config' folder """

    currentPath = os.path.realpath(__file__)
    configPath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(currentPath))),"local_config")
    assert os.path.exists(configPath), "Missing 'local_config' folder beside 'usit' folder"
    return configPath


def getDriversPath(LOCAL_CONFIG_PATH):
    
    """ Returns the path located in the configuration file "drivers_path.txt" """
    
    filePath = os.path.join(LOCAL_CONFIG_PATH,"drivers_path.txt")
    assert os.path.exists(filePath), "Missing drivers_path.txt configuration file"
    with open(filePath,"r") as fileHandle :
        driversPath = fileHandle.read().strip('\n')
    driversPath = os.path.realpath(driversPath)
    assert os.path.exists(driversPath), "Path provided in drivers_path.txt doesn't exist"
    return driversPath




def getDevicesIndex(LOCAL_CONFIG_PATH):
    
    """ Return the content of the 'devices_index.txt' content in a pandas dataframe """
    
    filePath = os.path.join(LOCAL_CONFIG_PATH,'devices_index.txt')
    assert os.path.exists(filePath), "Missing file devices_index.txt beside the drivers folder"
    index = pd.read_csv(filePath,sep=',',header=None,names=['name','driver','address'])
    
    assert len(index.name) == len(index.name.unique()), "Check your devices_index.txt file: 2 devices cannot have the same name."


    index.set_index(['name'],inplace=True)
    
    for driverName in index.driver.unique() :
        if isDriver(driverName) is False :
            index = index[index.driver != driverName]
    return index








def isDriver(driver_name) :
    
    """ Test if the provided name corresponds to a correct driver folder """
    
    try : 
        
        # The provided path has to be a folder
        path = os.path.join(DRIVER_PATH,driver_name)
        assert os.path.isdir(path), "Not a folder"
        
        # Which contains at least 2 python script : 
        # - the driver itself with the same name as the folder
        # - the configuration script usit_config.py
        basename = os.path.basename(path)
        for fileName in [basename + ".py","usit_config.py"] : assert fileName in os.listdir(path), f"No {fileName} file"
    
        return True
    
    except Exception as e :
        return False
    
    
def getLibrary(driver_path):
    
    """ Open the library located at the path provided """
    
    assert os.path.isfile(driver_path)
    basename = os.path.basename(driver_path)
    spec = importlib.util.spec_from_file_location(basename, driver_path)
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    return lib
    
def getDeviceClass(device_name):
    
    """ Returns the class Device (not instantiated) located in the driver script """
    
    driver_name = DEVICES_INDEX.loc[device_name,'driver']
    path = os.path.join(DRIVER_PATH,driver_name,driver_name+".py")
    assert os.path.exists(path), f"This is not a correct device folder (no file {driver_name}.py)"
    lib = getLibrary(path)
    assert hasattr(lib,'Device'), "There is no class 'Device' in the driver script"
    assert inspect.isclass(lib.Device), "The object 'Device' is not a class in the driver script"
    return lib.Device
    
def getConfigFunc(driver_name):
    
    """ Returns the function 'configure' located in the script usit_config.py in the driver folder """

    path = os.path.join(DRIVER_PATH,driver_name,'usit_config.py')
    assert os.path.exists(path), "This is not a correct device folder (no file usit_config.py)"
    lib = getLibrary(path)
    assert hasattr(lib,'configure'), "There is no function 'configure' in the script usit_config.py"
    assert inspect.isfunction(lib.configure), "The object 'configure' is not a function in the script usit_config.py"
    return lib.configure

def getDeviceMaterial(driver_name):
    
    """ Return the class 'Device' instantiated with the provided address, 
    and the function 'configure' of the driver """
    
    assert driver_name in get_devices(), "Device {driver_name} not existing in the index"
    address = str(DEVICES_INDEX.loc[driver_name,'address'])
    instance = getDeviceClass(driver_name)(address)
    return instance, getConfigFunc(driver_name)
    


def get_devices():
    return list(DEVICES_INDEX.index)
    
    
LOCAL_CONFIG_PATH = getLocalConfigPath()
DRIVER_PATH = getDriversPath(LOCAL_CONFIG_PATH)
DEVICES_INDEX = getDevicesIndex(LOCAL_CONFIG_PATH)
    
    
    
    