# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 10:02:22 2019

@author: qchat
"""

import os
import importlib
import inspect

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
    


def loadDevice(deviceName):
    
    """ Return the class 'Device' instantiated with the provided address, 
    and the function 'configure' of the driver """
    
    index = usit.core.devices.index[deviceName]
    driverName = index['driver']
    
    driver_path = os.path.join(usit.core.DRIVERS_PATH,driverName,f'{driverName}.py')
    driver = getLibrary(driver_path)
        
    # Check if Device class exists in the driver
    className = 'Device'
    if 'class' in index.keys() :
        className = index['class']
    assert hasattr(driver,className), f"There is no class {className} in the driver script"
    driverClass = getattr(driver,className)
    assert inspect.isclass(driverClass), f"The object {className} is not a class in the driver script"

    # kwargs creation
    kwargs = dict(index)
    del kwargs['driver']
    if 'class' in kwargs.keys() : del kwargs['class']
    instance = driverClass(**kwargs)
    
    return instance
    