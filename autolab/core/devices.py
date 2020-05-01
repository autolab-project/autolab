# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:25:49 2019

@author: quentin.chateiller
"""


from . import drivers
from .elements import Module
from .utilities import emphasize
from . import config

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



def get_final_device_config(device_name,**kwargs) :

    ''' Returns a valid device config from configuration file overwritten by kwargs '''

    if device_name in config.list_all_devices_configs() :

        # Load config object
        device_config = dict(config.get_device_config(device_name))

        # Overwrite config with provided configuration in kwargs
        for key,value in kwargs.items() :
            device_config[key] = value

    else :

        # Create config object
        device_config = kwargs

    # And the argument connection has to be provided
    assert 'driver' in device_config.keys(), f"Missing driver name for device '{device_name}'"
    assert 'connection' in device_config.keys(), f"Missing connection type for device '{device_name}'"

    return device_config



def get_device(device_name, **kwargs):

    ''' Returns the Device associated to device_name. Load it if not already done.'''

    device_config = get_final_device_config(device_name, **kwargs)

    if device_name in list_loaded_devices() :
        assert device_config == DEVICES[device_name].device_config, f'You cannot change the configuration of an existing Device. Close it first & retry, or remove the provided configuration.'

    else :
        instance = drivers.get_driver(device_config['driver'],
                                       device_config['connection'],
                                       **{ k:v for k,v in device_config.items() if k not in ['driver','connection']})
        DEVICES[device_name] = Device(device_name,instance,device_config)
        DEVICES[device_name].device_config = device_config

    return DEVICES[device_name]




# =============================================================================
# DEVICES LIST HELP
# =============================================================================

def list_loaded_devices():

    ''' Returns the list of the loaded devices '''

    return list(DEVICES.keys())


def list_devices():

    ''' Returns the list of all configured devices '''

    return config.list_all_devices_configs()





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
