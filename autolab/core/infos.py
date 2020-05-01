# -*- coding: utf-8 -*-

from . import config as _config
from . import stats as _stats
from . import drivers as _drivers
from . import paths as _path
from . import utilities as _utilities
from . import devices as _devices

# =============================================================================
# INFOS
# =============================================================================

def list_drivers(_print=True):

    ''' Returns a list of all the drivers with categories by sections (autolab drivers, local drivers) '''

    _drivers.update_drivers_paths()

    s = '\n'
    s += f'{len(_drivers.DRIVERS_PATHS)} drivers found\n\n'

    for source_name in _paths.DRIVER_SOURCES.keys() :
        sub_driver_list = sorted([key for key in _drivers.DRIVERS_PATHS.keys() if _drivers.DRIVERS_PATHS[key]['source']==source_name])
        s += f'Drivers in {_paths.DRIVER_SOURCES[source_name]}:\n'
        txt_list = [[f'    - {driver_name}',f'({_drivers.get_driver_category(driver_name)})']
                     for driver_name in sub_driver_list ]
        s += _utilities.two_columns(txt_list)+'\n\n'

    if _print is True : print(s)
    else : return s

def list_devices(_print=True):

    ''' Returns a list of all the devices and their associated drivers from devices_config.ini '''

    # Gather local config informations
    devices_names        = _devices.list_devices()
    devices_names_loaded = _devices.list_loaded_devices()

    # Build infos str for devices
    s = '\n'
    s += f'{len(devices_configs)} devices found\n\n'
    txt_list = [[f'    - {name} '+('[loaded]' if name in devices_names_loaded else ''),
                 f'({_config.get_device_config(name)["driver"]})']
                 for name in devices_names ]
    s += _utilities.two_columns(txt_list)+'\n'

    if _print is True : print(s)
    else : return s


def infos(_print=True):

    ''' Returns a list of all the drivers and all the devices (along with their associated drivers from devices_config.ini) '''

    s  = ''
    s += list_drivers(_print=_print)
    s += list_devices(_print=_print)

    if _print is False : return s


# =============================================================================
# DRIVERS
# =============================================================================

def config_help(driver_name, _print=True, _parser=False):

    ''' Display the help of a particular driver (connection types, modules, ...) '''

    # Load list of all parameters
    driver_lib = _drivers.load_driver_lib(driver_name)
    params = {}
    params['driver'] = driver_name
    params['connection'] = {}
    for conn in _drivers.get_connection_names(driver_lib) :
        params['connection'][conn] = _drivers.get_class_args(_drivers.get_connection_class(driver_lib,conn))
    params['other'] = _drivers.get_class_args(get_driver_class(driver_lib))
    if hasattr(_drivers.get_driver_class(driver_lib),'slot_config') :
        params['other']['slot1'] = f'{_drivers.get_driver_class(driver_lib).slot_config}'
        params['other']['slot1_name'] = 'my_<MODULE_NAME>'

    mess = '\n'

    # Name and category if available
    submess = f'Driver "{driver_name}" ({_drivers.get_driver_category(driver_name)})'
    mess += _utilities.emphasize(submess,sign='=') + '\n'

    # Connections types
    c_option=''
    if _parser: c_option='(-C option)'
    mess += f'\nAvailable connections types {c_option}:\n'
    for connection in params['connection'].keys() :
        mess += f' - {connection}\n'
    mess += '\n'

    # Modules
    if hasattr(_drivers.get_driver_class(driver_lib),'slot_config') :
        mess += 'Available modules:\n'
        modules = _drivers.get_module_names(driver_lib)
        for module in modules :
            moduleClass = _drivers.get_module_class(driver_lib,module)
            mess += f' - {module}'
            if hasattr(moduleClass,'category') : mess += f' ({moduleClass.category})'
            mess += '\n'
        mess += '\n'

    # Example of get_driver
    mess += '\n' + _utilities.underline('Loading a Device manually (with arguments):') + '\n\n'
    for conn in params['connection'].keys() :
        if _parser is False :
            args_str = f"'{params['driver']}', connection='{conn}'"
            for arg,value in params['connection'][conn].items():
                args_str += f", {arg}='{value}'"
            for arg,value in params['other'].items():
                args_str += f", {arg}='{value}'"
            mess += f"   a = autolab.get_device({args_str})\n"
        else :
            args_str = f"-D {params['driver']} -C {conn} "
            for arg,value in params['connection'][conn].items():
                if arg == 'address' : args_str += f"-A {value} "
                if arg == 'port' : args_str += f"-P {value} "
            if len(params['other'])>0 : args_str += '-O '
            for arg,value in params['other'].items():
                args_str += f"{arg}={value} "
            mess += f"   autolab device {args_str} \n"

    # Example of a devices_config.ini section
    mess += '\n\n' + _utilities.underline('Saving a Device configuration in devices_config.ini:') + '\n'
    for conn in params['connection'].keys() :
        mess += f"\n   [my_{params['driver']}]\n"
        mess += f"   driver = {params['driver']}\n"
        mess += f"   connection = {conn}\n"
        for arg,value in params['connection'][conn].items():
            mess += f"   {arg} = {value}\n"
        for arg,value in params['other'].items():
            mess += f"   {arg} = {value}\n"

    # Example of get_driver_by_config
    mess += '\n\n' + _utilities.underline('Loading a Device using a configuration in devices_config.ini:') + '\n\n'
    if _parser is False :
        mess += f"   a = autolab.get_device('my_{params['driver']}')"
    else :
        mess += f"   autolab device -D my_{params['driver']}\n"

    mess += "\n Note: provided arguments overwrite those found in devices_config.ini"

    if _print is True : print(mess)
    else : return mess


# =============================================================================
# STATS
# =============================================================================

def stats():

    ''' Display short message about stats management from autolab and actual stats collection state '''

    state_str = 'ENABLED' if _stats.is_stats_enabled() else 'DISABLED'
    return _stats.startup_text + f'\n\nCurrent state: [{state_str}]'
