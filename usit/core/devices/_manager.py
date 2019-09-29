# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:25:49 2019

@author: quentin.chateiller
"""


from ._elements import Device
from ._loader import loadDevice

import usit

class DeviceManager() :
    
    """ This class manage the different devices """
    
    
    
    def __init__(self):
        
        self._dev = {}
        
        # Initial creation of raw Device objects 
        for name in usit.core.devices.index.sections() :
            self._dev[name] = Device(self,name)
            
            
    
    def list(self):
        
        """ Returns the list of available devices """
        
        return list(self._dev.keys())
    
    

    def get_loaded_devices(self):
        
        """ Returns the list of the devices already loaded """
        
        return [ name for name in self.list() if self._isLoaded(name) ]
    
    
    
    def _isLoaded(self,name):
        
        """ Test is a device is already loaded """
        
        return self._dev[name]._instance is not None
    
    
    
    def getElementByAddress(self,address):
        
        """ Return the element located at the provided address """
        
        address = address.split('.')
        
        try : 
            element = getattr(self,address[0])
            for addressPart in address[1:] :
                element = getattr(element,addressPart)
            return element
        except :
            pass
            
            
        
        
        
    
    # REPRESENTATION
    # =========================================================================
    
    def __dir__(self):
        
        """ For auto-completion """
        
        return self.list() + ['list', 'close_all', 'info']
    
    
    
    def info(self):
        
        """ This function prints informations for the user about the availables devices """
        
        txt = "Availables devices:\n-------------------\n"
        for name in self.list():
            txt += f" - {name}"
            if self._isLoaded(name) : txt += ' [loaded]'
            txt += "\n"
        print(txt)
    
    
    
    
    
    
    
    # GET AND CLOSE DEVICE
    # =========================================================================

    def __getattr__(self,name):
        
        assert name in self.list(), f"No device with name {name} in the device index"
        if self._isLoaded(name) is False :
            self._load(name)
        return self._dev[name]
       
        
    
    def close_all(self):
        
        """ This function close the connection of all the loaded devices """
        
        for devName in self.get_loaded_devices() :
            self._dev[devName].close()
        
        
        
    def _load(self,name):
        
        """ This function tries to load the devices with the following name """
        
        instance = loadDevice(name)
        self._dev[name].load(instance)

