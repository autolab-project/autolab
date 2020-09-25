# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:25:49 2019

@author: quentin.chateiller
"""


import autolab
from .elements import Module
from .utilities import emphasize

# Storage of the devices
DEVICES = {}


def get_element_by_address(address):
    
    """ Returns the Element located at the provided address """
    
    address = address.split('.')
    
    try :
        element = get_device(address[0])
        for addressPart in address[1:] :
            element = getattr(element,addressPart)
        return element
    except :
        pass
        


def get_device(name, **kwargs):
    
    ''' Returns the Device associated to device_name. Load it if not already done.'''
    
    if name in DEVICES.keys() :
        assert len(kwargs)==0, f'You cannot change the configuration of an existing Device. Close it first & retry, or remove the provided configuration.'
    else : 
        instance = autolab.get_driver(name,**kwargs)
        DEVICES[name] = Device(name,instance)

    return DEVICES[name]
    
    
    
    
# =============================================================================
# DEVICES LIST HELP
# =============================================================================
        


def list_devices():
    
    ''' Returns the list of the loaded devices '''
    
    return list(DEVICES.keys())





# =============================================================================
# DEVICE CLASS
# =============================================================================

class Device(Module):
    
    def __init__(self,device_name,instance):
                
        Module.__init__(self,None,{'name':device_name,
                                   'object':instance,
                                   'help':f'Device {device_name}'})
        
    def close(self):
        
        """ This function close the connection of the current physical device """
        
        try : self.instance.close()
        except : pass
        del DEVICES[self.name]
        
        
    def __dir__(self):
        
        """ For auto-completion """
        
        return  self.list_modules() + self.list_variables() + self.list_actions() + ['close','help','instance']
 
        
    
    
    


