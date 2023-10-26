# -*- coding: utf-8 -*-

from . import config
from . import stats
from . import drivers
from . import paths
from . import utilities
from . import devices

# =============================================================================
# INFOS
# =============================================================================

def list_drivers(_print=True):

    ''' Returns a list of all the drivers with categories by sections (autolab drivers, local drivers) '''

    drivers.update_drivers_paths()

    s = '\n'
    s += f'{len(drivers.DRIVERS_PATHS)} drivers found\n\n'

    for source_name in paths.DRIVER_SOURCES.keys() :
        sub_driver_list = sorted([key for key in drivers.DRIVERS_PATHS.keys() if drivers.DRIVERS_PATHS[key]['source']==source_name])
        s += f'Drivers in {paths.DRIVER_SOURCES[source_name]}:\n'
        if len(sub_driver_list)>0 :
            txt_list = [[f'    - {driver_name}',f'({drivers.get_driver_category(driver_name)})']
                        for driver_name in sub_driver_list ]
            s += utilities.two_columns(txt_list)+'\n\n'
        else :
            s += '    <No drivers>'

    if _print is True : print(s)
    else : return s


def list_devices(_print=True):

    ''' Returns a list of all the devices and their associated drivers from devices_config.ini '''

    # Gather local config informations
    devices_names        = devices.list_devices()
    devices_names_loaded = devices.list_loaded_devices()

    # Build infos str for devices
    s = '\n'
    s += f'{len(devices_names)} devices found\n\n'
    txt_list = [[f'    - {name} '+('[loaded]' if name in devices_names_loaded else ''),
                 f'({config.get_device_config(name)["driver"]})']
                 for name in devices_names ]
    s += utilities.two_columns(txt_list)+'\n'

    if _print is True : print(s)
    else : return s


def infos(_print=True):

    ''' Returns a list of all the drivers and all the devices, along with their associated drivers from devices_config.ini '''

    s  = ''
    s += list_drivers(_print=False)
    s += list_devices(_print=False)

    if _print is True : print(s)
    else : return s

# =============================================================================
# DRIVERS
# =============================================================================

def config_help(driver_name, _print=True, _parser=False):

    ''' Display the help of a particular driver (connection types, modules, ...) '''
    try:
        driver_name = devices.get_final_device_config(driver_name)["driver"]
    except:
        pass
    # Load list of all parameters
    driver_lib = drivers.load_driver_lib(driver_name)
    params = {}
    params['driver'] = driver_name
    params['connection'] = {}
    for conn in drivers.get_connection_names(driver_lib) :
        params['connection'][conn] = drivers.get_class_args(drivers.get_connection_class(driver_lib,conn))
    params['other'] = drivers.get_class_args(drivers.get_driver_class(driver_lib))
    if hasattr(drivers.get_driver_class(driver_lib),'slot_config') :
        params['other']['slot1'] = f'{drivers.get_driver_class(driver_lib).slot_config}'
        params['other']['slot1_name'] = 'my_<MODULE_NAME>'

    mess = '\n'

    # Name and category if available
    submess = f'Driver "{driver_name}" ({drivers.get_driver_category(driver_name)})'
    mess += utilities.emphasize(submess,sign='=') + '\n'

    # Connections types
    c_option=''
    if _parser: c_option='(-C option)'
    mess += f'\nAvailable connections types {c_option}:\n'
    for connection in params['connection'].keys() :
        mess += f' - {connection}\n'
    mess += '\n'

    # Modules
    if hasattr(drivers.get_driver_class(driver_lib),'slot_config') :
        mess += 'Available modules:\n'
        modules = drivers.get_module_names(driver_lib)
        for module in modules :
            moduleClass = drivers.get_module_class(driver_lib,module)
            mess += f' - {module}'
            if hasattr(moduleClass,'category') : mess += f' ({moduleClass.category})'
            mess += '\n'
        mess += '\n'

    # Example of a devices_config.ini section
    mess += '\n\n' + utilities.underline('Saving a Device configuration in devices_config.ini:') + '\n'
    for conn in params['connection'].keys() :
        mess += f"\n   [my_{params['driver']}]\n"
        mess += f"   driver = {params['driver']}\n"
        mess += f"   connection = {conn}\n"
        for arg,value in params['connection'][conn].items():
            mess += f"   {arg} = {value}\n"
        for arg,value in params['other'].items():
            mess += f"   {arg} = {value}\n"

    # Example of get_driver
    mess += '\n' + utilities.underline('Loading a Driver:') + '\n\n'
    for conn in params['connection'].keys() :
        if _parser is False :
            args_str = f"'{params['driver']}', connection='{conn}'"
            for arg,value in params['connection'][conn].items():
                args_str += f", {arg}='{value}'"
            for arg,value in params['other'].items():
                if type(value) is str:
                    args_str += f", {arg}='{value}'"
                else:
                    args_str += f", {arg}={value}"
            mess += f"   a = autolab.get_driver({args_str})\n"
        else :
            args_str = f"-D {params['driver']} -C {conn} "
            for arg,value in params['connection'][conn].items():
                if arg == 'address' : args_str += f"-A {value} "
                if arg == 'port' : args_str += f"-P {value} "
            if len(params['other'])>0 : args_str += '-O '
            for arg,value in params['other'].items():
                args_str += f"{arg}={value} "
            mess += f"   autolab driver {args_str} -m method(value) \n"

    # Example of get_device
    mess += '\n\n' + utilities.underline('Loading a Device configured in devices_config.ini:') + '\n\n'
    if _parser is False :
        mess += f"   a = autolab.get_device('my_{params['driver']}')"
    else :
        mess += f"   autolab device -D my_{params['driver']} -e element -v value \n"

    if _print is True : print(mess)
    else : return mess




# =============================================================================
# STATS
# =============================================================================

def statistics(_print=True):

    ''' Display short message about stats management from autolab and actual stats collection state '''

    state_str = 'ENABLED' if stats.is_stats_enabled() else 'DISABLED'
    mess = stats.startup_text + f'\n\nCurrent state: [{state_str}]'

    if _print is True : print(mess)
    else : return mess
