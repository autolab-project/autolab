# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:25:49 2019

@author: quentin.chateiller
"""

from typing import List, Union

from .drivers import get_driver_path, get_driver
from .config import list_all_devices_configs, get_device_config
from .elements import Module, Element

# Storage of the devices
DEVICES = {}

# After DEVICES to avoid circular import
from .variables import update_allowed_dict

# =============================================================================
# DEVICE CLASS
# =============================================================================

class Device(Module):

    def __init__(self, device_name: str, instance, device_config: dict):
        """ device_config is returned by :meth:`get_final_device_config` """

        self.device_config = device_config  # hidden from completion
        self.driver_path = get_driver_path(device_config["driver"])

        super().__init__(None, {'name': device_name, 'object': instance,
                                'help': f'Device {device_name} at {self.driver_path}'})

    def close(self):
        """ This function close the connection of the current physical device """
        # Remove read and write signals from gui
        try:
            # condition avoid reopenning connection if use close twice
            if self.name in DEVICES:
                for struc in self.get_structure():
                    element = get_element_by_address(struc[0])
                    if struc[1] == 'variable':
                        element._read_signal = None
                        element._write_signal = None
                    if struc[1] == 'action':
                        element._write_signal = None
        except: pass

        try: self.instance.close()
        except: pass

        del DEVICES[self.name]
        update_allowed_dict()

    def __dir__(self):
        """ For auto-completion """
        return (self.list_modules() + self.list_variables()
                + self.list_actions() + ['driver_path', 'close', 'help', 'instance'])


# =============================================================================
# DEVICE GET FUNCTION
# =============================================================================

def get_element_by_address(address: str) -> Element:
    """ Returns the Element located at the provided address """
    address_list = address.split('.')
    device_name = address_list[0]
    if device_name in DEVICES:
        element = DEVICES[device_name]
    else:
        # This should not be used on autolab closing to avoid access violation due to config opening
        element = get_device(device_name)

    for i, address_part in enumerate(address_list[1: ]):
        address_part = address_part.replace(' ', '')
        if hasattr(element, address_part):
            element = getattr(element, address_part)
        else:
            raise AttributeError(
                f"'{address_part}' not found in '{'.'.join(address_list[: i+1])}'.")
    return element


def get_final_device_config(device_name: str, **kwargs) -> dict:
    ''' Returns a valid device config from configuration file overwritten by kwargs '''
    assert device_name in list_all_devices_configs(), f"Device name '{device_name}' not found in devices_config.ini"

    # Load config object
    device_config = dict(get_device_config(device_name))

    # Overwrite config with provided configuration in kwargs
    for key, value in kwargs.items():
        device_config[key] = value

    # And the argument connection has to be provided
    assert 'driver' in device_config, f"Missing driver name for device '{device_name}'"

    if device_config['driver'] == 'autolab_server':
        device_config['connection'] = 'USELESS_ENTRY'

    assert 'connection' in device_config, f"Missing connection type for device '{device_name}'"

    return device_config


def get_device(device_name: str, **kwargs) -> Device:
    ''' Returns the Device associated to device_name. Load it if not already done.'''
    device_config = get_final_device_config(device_name, **kwargs)

    if device_name in list_loaded_devices():
        assert device_config == DEVICES[device_name].device_config, 'You cannot change the configuration of an existing Device. Close it first & retry, or remove the provided configuration.'

    else:
        instance = get_driver(
            device_config['driver'], device_config['connection'],
            **{k: v for k, v in device_config.items() if k not in [
                'driver', 'connection']})
        DEVICES[device_name] = Device(device_name, instance, device_config)
        update_allowed_dict()

    return DEVICES[device_name]


# =============================================================================
# DEVICES LIST HELP
# =============================================================================

def list_loaded_devices() -> List[str]:
    ''' Returns the list of loaded device names '''
    return list(DEVICES)


def list_devices() -> List[str]:
    ''' Returns the list of all configured device names '''
    return list_all_devices_configs()


def get_devices_status() -> dict:
    ''' Returns a dict of devices as keys and True/False values if device is loaded'''

    devices_names = list_devices()
    loaded_devices_names = list_loaded_devices()

    return {k: (k in loaded_devices_names) for k in devices_names}


# =============================================================================
# CLOSE DEVICES
# =============================================================================

def close(device: Union[str, Device] = "all"):
    """ Close a device by providing its name or its instance. Use 'all' to close all openned devices. """

    if str(device) == "all":
        for device_name in list_loaded_devices():
            try:
                DEVICES[device_name].close()
            except Exception:
                print(f"Warning: device '{device_name}' has not been closed properly")

    elif isinstance(device, Device):
        if device.name in DEVICES:
            device.close()
        else:
            print(f"No device '{device.name}' in {list_loaded_devices()}")

    elif isinstance(device, str):
        if device in DEVICES:
            DEVICES[device].close()
        else:
            print(f"No device '{device}' in {list_loaded_devices()}")

    else:
        var_type = str(type(device)).split("'")[1]
        print(f"Warning, {device} with type '{var_type}' is not a reconized device")
