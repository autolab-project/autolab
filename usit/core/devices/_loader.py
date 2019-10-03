# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 10:02:22 2019

@author: qchat
"""



import usit  


def loadDevice(deviceName):
    
    """ Return the class 'Device' instantiated with the provided address, 
    and the function 'configure' of the driver """
    
    index = usit.core.devices.index[deviceName]
    driverName = index['driver']

    driver = getattr(usit.drivers,driverName)
        
    # Check if Device class exists in the driver
    assert 'connection' in index.keys(), f"Missing connection type"
    connection = index['connection']
    assert connection in driver._getConnectionNames(),f"There is no connection '{connection}' available in the driver script"
    driver._getConnectionClass(connection)
    driverClass = driver._getConnectionClass(connection)

    # kwargs creation
    kwargs = dict(index)
    del kwargs['driver']
    if 'connection' in kwargs.keys() : del kwargs['connection']
    instance = driverClass(**kwargs)
    
    return instance
    