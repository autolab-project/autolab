# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import os

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)),'autolab','core'))
import paths
import index
import drivers_parser_utilities
import config as local_config


PATHS     = paths.Paths()
UTILITIES = drivers_parser_utilities.utilities()

def main():
    # Initial parser for command line arguments (help finding the device and associated modules)
    accepted_arguments = ['-l','-i','-d']
    args_to_pass,temp_args = init_argument_to_parse(accepted_arguments=accepted_arguments)    
    # Parser configuration can be use to write common options that won't be used by the first one
    parser = ArgumentParser(add_help=False)
    parser.add_argument("-d", "--driver", type=str, dest="driver", default=None, help="Set the nickname or driver to use: 1) uses nickname if it is defined in devices_index.ini OR(if it is not) 2) Set the driver name to use." )
    parser.add_argument("-l", "--link", type=str, dest="link", default=None, help="Set the link to use for the connection." )
    parser.add_argument("-i", "--address", type=str, dest="address", default=None, help="Set the address to use for the communication." )
    parser.add_argument("-m", "--methods", nargs='+', dest="methods", default=None, help="Set the methods to use." )
    args = parser.parse_args(args_to_pass)
    
    # Load devices_index.ini to find potentially defined devices (-i nickname option to use)
    local_config.check(PATHS)
    configparser = index.load(PATHS)
    # Load the device or the driver
    if args.driver in configparser.sections():
        section = configparser[args.driver]
        
        # WARNING will choose arguments provided by the user instead of devices_index.ini ones        
        if args.link: pass
        else: 
            assert 'connection' in section.keys(), f"Connection section: Missing connection type for device '{args.driver}'"
            args.link = section['connection']
        if args.address: pass
        else: 
            assert 'address' in section.keys(), f"Address section: Missing address for device '{args.driver}'"
            args.address = section['address']
        args.driver = section['driver']

        kwargs = dict(section)
        del kwargs['driver']; del kwargs['connection']; del kwargs['address']
    else:
        assert args.driver, f"Missing driver name to use"
        if len(temp_args)>1:
            if not(temp_args[1] == '-h' and temp_args[0].startswith('-d')):
                assert args.link and args.address, f"Missing address or connection type. Provided are, type: {args.link}, address: {args.address}"
        else:
            assert args.link and args.address, f"Missing address or connection type. Provided are, type: {args.link}, address: {args.address}"
        kwargs = {}
    
    # A path to sys path at index 0
    update_path(args)
        
    # Import the parser module
    Driver_parser_module = import_parser_module(args)
    
    # Second help for connection classes -l option
    if len(temp_args)>1:
        if temp_args[1] == '-h' and temp_args[0].startswith('-d'):
            Driver_module = import_driver_module(args)
            print_help_connections(Driver_module) 
    
    # Instance the driver (establish communication with the physical device)
    Instance = Driver_parser_module.Driver_parser(args,UTILITIES,**kwargs)
    
    # Add arguments to the existing parser (driver dependant)
    parser = Instance.add_parser_arguments(parser)
    args = parser.parse_args()
    
    # Finally, execute functions according to the arguments provided
    Instance.do_something(args)

def import_parser_module(args):
    try: Driver_parser_module = __import__(f'{args.driver}_parser')
    except ModuleNotFoundError: print(f'No module found. List of the inspected folder:{os.listdir()}');sys.exit()
    globals()[Driver_parser_module] = Driver_parser_module
    return Driver_parser_module

def import_driver_module(args):
    try: Driver_module = __import__(f'{args.driver}')
    except ModuleNotFoundError: print(f'No module found. List of the inspected folder:{os.listdir()}');sys.exit()
    globals()[Driver_module] = Driver_module
    return Driver_module

def update_path(args):
    Driver_path = [os.path.join(PATHS.DRIVERS_PATHS[key],args.driver) for key in PATHS.DRIVERS_PATHS.keys() if os.path.exists(os.path.join(PATHS.DRIVERS_PATHS[key],args.driver))]
    assert len(Driver_path) != 0, f"Warning: No driver found, full path was: {Driver_path}"
    assert len(Driver_path) == 1, f"Warning: More than one folder found with paths: {Driver_path}"
    Driver_path = Driver_path[0]
    
    sys.path.insert(0,Driver_path)  # Insert Driver's path at the first place of the list!
    
def init_argument_to_parse(accepted_arguments):
    args = sys.argv[1:]  # [1:] to remove module name
    args = ''.join(args)
    args =  ["-"+arg for arg in args.split("-") if arg]
    if args[0] == '-h': print_help_message()  # if first argument is -h print autolab-driver's help message
    args_to_pass =  [arg   for arg in args   for acc in accepted_arguments   if acc in arg]
    return args_to_pass,args

def print_help_message():
    print(f"""
----------------  General informations:  ----------------

This is a very basic help for usage of autolab-drivers. More info can be found on read the doc website. To display a more extensive version please provide enough arguments to establish connection with the device.
    
    Usage:   autolab-drivers -d driver_name -l connection -i address -h

Recquiered arguments to establish the connection:
    -d driver_name: name of the driver to use (e.g.: agilent_33220A). driver_name can be either the driver_name or the defined nickname, as defined by the user in the devices_index.ini. See lower for the list of available drivers.
    -l name of the connection to use to communicate with the device (e.g.: VISA, VXI11, SOCKET, TELNET, USB, GPIB, ...). You may access the available connections types with an help (see lower section).
    -i address: full address to reach the device that depends on the connection type (e.g.: 192.168.0.2  [for VXI11])
    
    
----------------  Helps (-h option)  ----------------       

Three helps are configured:
    autolab-drivers -h
    This help message.
    
    autolab-drivers -d driver_name -h 
    Short message displaying the implemented connections to a device (VISA, etc).
    
    autolab-drivers -d driver_name -l connection -i address -h
    Full help message about the driver.
    
    
----------------  List of available drivers (-d option) ----------------
 
    {available_drivers()}
    
    """)
    sys.exit()

def print_help_connections(driver_module):
    print(f"""
----------------  Connections types for {driver_module.__name__} (-d option) ----------------

    {available_connection_classes(driver_module)}
    
    """)
    sys.exit()

def available_drivers():
    s = ''; flag = 0
    for key in PATHS.DRIVERS_PATHS.keys():
        if flag !=0:
            s = s + f'\n\n    - Location (do not specify in the command):  {PATHS.DRIVERS_PATHS[key]}\n    '
        else:
            s = s + f'- Location (do not specify in the command):  {PATHS.DRIVERS_PATHS[key]}\n    '
        temp = [i for i in os.listdir(PATHS.DRIVERS_PATHS[key]) if i and not i.startswith('_')]; temp.sort();
        if len(temp)==0: s=s+'None'
        else: s = s + ', '.join(temp) 
        flag = flag + 1
    return s

def available_connection_classes(module):
    import inspect
    return ', '.join([name.replace('Driver_','') for name, obj in inspect.getmembers(module, inspect.isclass) if obj.__module__ is module.__name__ if name.startswith('Driver_')])
    
    
    
