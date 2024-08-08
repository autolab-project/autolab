# -*- coding: utf-8 -*-
import sys

from .config import get_device_config
from .drivers import (update_drivers_paths, DRIVERS_PATHS, get_driver_category,
                      load_driver_lib, get_connection_names, get_class_args,
                      get_connection_class, get_driver_class, get_module_names,
                      get_module_class)
from .paths import DRIVER_SOURCES
from .utilities import two_columns, emphasize, underline
from .devices import list_devices, list_loaded_devices, get_final_device_config

# =============================================================================
# INFOS
# =============================================================================

def _list_drivers(_print: bool = True) -> str:
    ''' Returns a list of all the drivers with categories by sections
    (autolab drivers, local drivers) '''
    update_drivers_paths()

    s = '\n'
    s += f'{len(DRIVERS_PATHS)} drivers found\n\n'

    for i, (source_name, source) in enumerate(DRIVER_SOURCES.items()):
        sub_driver_list = sorted([key for key, val in DRIVERS_PATHS.items(
            ) if val['source'] == source_name])
        s += f'Drivers in {source}:\n'
        if len(sub_driver_list) > 0:
            txt_list = [[f' - {driver_name}',
                         f'({get_driver_category(driver_name)})']
                            for driver_name in sub_driver_list]
            s += two_columns(txt_list) + '\n\n'
        else:
            if (i + 1) == len(DRIVER_SOURCES):
                s += ' <No drivers>\n\n'
            else:
                s += ' <No drivers> (or overwritten)\n\n'

    if _print:
        print(s)
        return None
    return s


def _list_devices(_print: bool = True) -> str:
    ''' Returns a list of all the devices and their associated drivers
    from devices_config.ini '''
    # Gather local config informations
    devices_names = list_devices()
    devices_names_loaded = list_loaded_devices()

    # Build infos str for devices
    s = '\n'
    s += f'{len(devices_names)} devices found\n\n'
    txt_list = [
        [f' - {name} ' + ('[loaded]' if name in devices_names_loaded else ''),
         f'({get_device_config(name)["driver"]})'] for name in devices_names]
    s += two_columns(txt_list) + '\n'

    if _print:
        print(s)
        return None
    return s


def infos(_print: bool = True) -> str:
    ''' Returns a list of all the drivers and all the devices,
    along with their associated drivers from devices_config.ini '''
    s  = ''
    s += _list_drivers(_print=False)
    s += _list_devices(_print=False)

    if _print:
        print(s)
        return None
    return s

# =============================================================================
# DRIVERS
# =============================================================================

def config_help(driver_name: str, _print: bool = True, _parser: bool = False) -> str:
    ''' Display the help of a particular driver (connection types, modules, ...) '''
    try:
        driver_name = get_final_device_config(driver_name)["driver"]
    except:
        pass
    # Load list of all parameters
    try:
        driver_lib = load_driver_lib(driver_name)
    except Exception as e:
        print(f"Can't load {driver_name}: {e}", file=sys.stderr)
        return None
    params = {}
    params['driver'] = driver_name
    params['connection'] = {}
    for conn in get_connection_names(driver_lib):
        params['connection'][conn] = get_class_args(
            get_connection_class(driver_lib, conn))
    params['other'] = get_class_args(get_driver_class(driver_lib))
    if hasattr(get_driver_class(driver_lib), 'slot_config'):
        params['other']['slot1'] = f'{get_driver_class(driver_lib).slot_config}'
        params['other']['slot1_name'] = 'my_<MODULE_NAME>'

    mess = '\n'

    # Name and category if available
    submess = f'Driver "{driver_name}" ({get_driver_category(driver_name)})'
    mess += emphasize(submess, sign='=') + '\n'

    # Connections types
    c_option=' (-C option)' if _parser else ''
    mess += f'\nAvailable connections types{c_option}:\n'
    for connection in params['connection']:
        mess += f' - {connection}\n'
    mess += '\n'

    # Modules
    if hasattr(get_driver_class(driver_lib), 'slot_config'):
        mess += 'Available modules:\n'
        modules = get_module_names(driver_lib)
        for module in modules:
            moduleClass = get_module_class(driver_lib, module)
            mess += f' - {module}'
            if hasattr(moduleClass, 'category'): mess += f' ({moduleClass.category})'
            mess += '\n'
        mess += '\n'

    # Example of a devices_config.ini section
    mess += '\n' + underline(
        'Saving a Device configuration in devices_config.ini:') + '\n'
    for conn in params['connection']:
        mess += f"\n[my_{params['driver']}]\n"
        mess += f"driver = {params['driver']}\n"
        mess += f"connection = {conn}\n"
        for arg, value in params['connection'][conn].items():
            mess += f"{arg} = {value}\n"
        for arg, value in params['other'].items():
            mess += f"{arg} = {value}\n"

    # Example of get_driver
    mess += '\n\n' + underline('Loading a Driver:') + '\n\n'
    for conn in params['connection']:
        if not _parser:
            args_str = f"'{params['driver']}', connection='{conn}'"
            for arg, value in params['connection'][conn].items():
                args_str += f", {arg}='{value}'"
            for arg, value in params['other'].items():
                if isinstance(value, str):
                    args_str += f", {arg}='{value}'"
                else:
                    args_str += f", {arg}={value}"
            mess += f"a = autolab.get_driver({args_str})\n"
        else:
            args_str = f"-D {params['driver']} -C {conn} "
            for arg,value in params['connection'][conn].items():
                if arg == 'address': args_str += f"-A {value} "
                if arg == 'port': args_str += f"-P {value} "
            if len(params['other']) > 0: args_str += '-O '
            for arg,value in params['other'].items():
                args_str += f"{arg}={value} "
            mess += f"autolab driver {args_str} -m method(value) \n"

    # Example of get_device
    mess += '\n\n' + underline(
        'Loading a Device configured in devices_config.ini:') + '\n\n'
    if not _parser:
        mess += f"a = autolab.get_device('my_{params['driver']}')"
    else:
        mess += f"autolab device -D my_{params['driver']} -e element -v value \n"

    if _print:
        print(mess)
        return None
    return mess
