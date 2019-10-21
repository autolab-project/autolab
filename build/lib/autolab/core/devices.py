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
        


def get_device(device_name):
    
    ''' Returns the Device associated to device_name. Load it if not already done.'''
    
    if device_name in DEVICES.keys() :
        return DEVICES[device_name]
    else :
        return Device(device_name)
    
    
    
    
    
# =============================================================================
# DEVICES LIST HELP
# =============================================================================
        
def list_devices():
    
    ''' Returns the list of the available devices names '''
    
    return list(autolab.list_driver_config())



def list_devices_loaded():
    
    ''' Returns the list of the loaded devices '''
    
    return list(DEVICES.keys())



def show_devices():
    
    ''' Display the help of the devices, that consists in a list of available
    devices, with an indication on their loaded state. '''
    
    txt = '\n'+emphasize('Available devices:')+'\n'
    for device_name in list_devices():
        txt += f" - {device_name}"
        if device_name in DEVICES.keys() : txt += ' [loaded]'
        txt += "\n"
        
    print(txt)





# =============================================================================
# DEVICE CLASS
# =============================================================================

class Device(Module):
    
    def __init__(self,device_name):
        
        assert device_name not in DEVICES.keys(), f'Device {device_name} is already open.'
        
        Module.__init__(self,None,{'name':device_name,
                                   'object':autolab.get_driver_by_config(device_name),
                                   'help':f'Device {device_name}'})

        DEVICES[self.name] = self
        
        
    def close(self):
        
        """ This function close the connection of the current physical device """
        
        try : self.instance.close()
        except : pass
        del DEVICES[self.name]
        
        
    def __dir__(self):
        
        """ For auto-completion """
        
        return  self.getModuleList() + self.getVariableList() + self.getActionList() + ['close','help','instance']
 
        
    
    
    


