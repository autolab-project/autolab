# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import os

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)),'autolab','core'))
import paths
import index
import drivers_parser_utilities
#import config as local_config
import autolab


UTILITIES = drivers_parser_utilities.utilities()

def main():
    # Initial parser for command line arguments (help finding the device and associated modules)
    accepted_arguments = ['-D','-A','-C']
    args_to_pass,temp_args = init_argument_to_parse(accepted_arguments=accepted_arguments)    
    # Parser configuration can be use to write common options that won't be used by the first one
    parser = ArgumentParser(add_help=False)
    parser.add_argument("-D", "--driver", type=str, dest="driver", default=None, help="Set the nickname or driver to use: 1) uses nickname if it is defined in local_config.ini OR(if it is not) 2) Set the driver name to use." )
    parser.add_argument("-C", "--connection", type=str, dest="connection", default=None, help="Set the connection to use for the connection." )
    parser.add_argument("-A", "--address", type=str, dest="address", default=None, help="Set the address to use for the communication." )
    
    parser.add_argument("-S","--slot", nargs='+', dest="slot", default=None, help="Set the slot configuration." )
    parser.add_argument("-P","--port", type=int, dest="port", default=None, help="Argument used to address different things depending on the connection type. SOCKET: the port number used to communicate, GPIB: the gpib board index, DLL: the path to the dll library." )
    parser.add_argument("-m", "--methods", nargs='+', dest="methods", default=None, help="Set the methods to use." )
    args = parser.parse_args(args_to_pass)

    # for adding --options, or options that must go through kwargs
    parser_additionnal = ArgumentParser(add_help=False,parents=[parser])
    parser_additionnal.add_argument("-h","--useless",action='store_false',dest="useless", default=None, help="Useless, avoid breaking")
    args_additionnal, unknown = parser_additionnal.parse_known_args()
    
    # Load local_config.ini to find potentially defined devices (-D nickname option to use)
    configparser = autolab.DRIVERS_CONFIG
    
    # Load the device or the driver
    if args.driver in configparser.sections():
        section = configparser[args.driver]
        # WARNING will choose arguments provided by the user instead of local_config.ini ones        
        # Mandatory arguments
        args.driver = section['driver']
        if args.connection: pass
        else: 
            assert 'connection' in section.keys(), f"Connection section: Missing connection type for device '{args.driver}'"
            args.connection = section['connection']
        
        kwargs = dict(section)
        del kwargs['driver']; del kwargs['connection']; 
        
        # Additionnal arguments
        if args.address: pass
        else: 
            if 'address' in section.keys():
                args.address = section['address']
                del kwargs['address']      
        # section slot* goes to kwargs (potentially overwriten by user lower)
        # -- options must be passed to kwargs (see lower)
    else:
        assert args.driver, f"Missing driver name to use"
        if len(temp_args)>1:
            if not(temp_args[0] == '-h' and temp_args[1].startswith('-D')):
                assert args.connection and args.address, f"Missing address or connection type. Provided are, type: {args.connection}, address: {args.address}"
        else:
            assert args.connection and args.address, f"Missing address or connection type. Provided are, type: {args.connection}, address: {args.address}"
        kwargs = {}
    # Arguments processing (slot must be in kwargs dict)
    if args_additionnal.port: kwargs['port'] = args_additionnal.port
    if args_additionnal.slot: 
        for slot in args_additionnal.slot:
            temp = slot.replace(' ','')
            kwargs[slot.split('=')[0]] = slot.split('=')[1]

    # A path to sys path at index 0
    Driver_path = update_path(args)
    
    # Second help for connection classes -C option
    if len(temp_args)>1:
        if temp_args[0] == '-h' and temp_args[1].startswith('-D'):
            Driver_module = import_module(f'{args.driver}',Driver_path)
            print_help_connections(Driver_module) 
        
    # Import the parser module
    Driver_parser_module = import_module(f'{args.driver}_parser',Driver_path)
    
    # Instance the driver (establish communication with the physical device)
    Instance = Driver_parser_module.Driver_parser(args,UTILITIES,**kwargs)
    
    # Add arguments to the existing parser (driver dependant)
    parser = Instance.add_parser_arguments(parser)
    args = parser.parse_args()
    
    # Finally, execute functions according to the arguments provided
    Instance.do_something(args)

def import_module(name,Driver_path):
    try: module = __import__(name)
    except ModuleNotFoundError: print(f'Module {name} not found. Files in the inspected folder:{os.listdir(Driver_path)}');sys.exit()
    globals()[module] = module
    return module

def update_path(args):
    Driver_path = [os.path.join(paths.DRIVER_SOURCES[key],args.driver) for key in paths.DRIVER_SOURCES.keys() if os.path.exists(os.path.join(paths.DRIVER_SOURCES[key],args.driver))]
    assert len(Driver_path) != 0, f"Warning: No driver found, full path was: {Driver_path}"
    assert len(Driver_path) == 1, f"Warning: More than one folder found with paths: {Driver_path}"
    Driver_path = Driver_path[0]
    
    sys.path.insert(0,Driver_path)  # Insert Driver's path at the first place of the list!
    return Driver_path
    
def init_argument_to_parse(accepted_arguments):
    args = sys.argv[1:]  # [1:] to remove module name
    args = ''.join(args)
    args =  ["-"+arg for arg in args.split("-") if arg]
    if len(args)>1: pass
    else: 
        if args[0] == '-h': print_help_message()  # if first argument is -h print autolab-driver's help message
    args_to_pass =  [arg   for arg in args   for acc in accepted_arguments   if acc in arg]
    return args_to_pass,args

def print_help_message():
    print(f"""
----------------  General informations:  ----------------

This is a very basic help message for usage of autolab-drivers. More info can be found on read the doc website. To display a more extensive further help please have a look at the section help below.
    
    Usage:   autolab-drivers -D driver_name -C connection -A address -h

Recquired connection arguments (capital letters):
    -D driver_name: name of the driver to use (e.g.: agilent_33220A). driver_name can be either the driver_name or the defined nickname, as defined by the user in the local_config.ini. See lower for the list of available drivers.
    -C connection type to use to communicate with the device (e.g.: VISA, VXI11, SOCKET, TELNET, USB, GPIB, ...). You may access the available connections types with an help (see below helps section).
    -A address: full address to reach the device that depends on the connection type (e.g.: 192.168.0.2  [for VXI11]) and on how you configured the device.
    
    
----------------  Helps (-h option)  ----------------       

Three helps are configured:
    autolab-drivers -h
    This help message.
    
    autolab-drivers -h -D driver_name
    Short message displaying the device category as well as the implemented connections to a device (VISA, etc).
    
    autolab-drivers -D driver_name -C connection -A address -h
    Full help message about the driver.
    
    
----------------  List of available drivers (-D option) ----------------
 
    {available_drivers()}
    
    """)
    sys.exit()

def print_help_connections(driver_module):
    print(f"""
----------------  Instrument category of {driver_module.__name__} (no option) ----------------
    {UTILITIES.get_category(driver_module=driver_module)}

----------------  Connections types for {driver_module.__name__} (-C option) ----------------

    {available_connection_classes(driver_module)}
    
    To get further help on the driver, you need to establish the connection by providing the appropriate address.
    
    """)
    sys.exit()
    

def available_drivers():
    s = ''; flag = 0
    for key in paths.DRIVER_SOURCES.keys():
        if flag !=0:
            s = s + f'\n\n    - Location (do not specify in the command):  {paths.DRIVER_SOURCES[key]}\n    '
        else:
            s = s + f'- Location (do not specify in the command):  {paths.DRIVER_SOURCES[key]}\n    '
        temp = [i for i in os.listdir(paths.DRIVER_SOURCES[key]) if i and not i.startswith('_')]; temp.sort();
        if len(temp)==0: s=s+'None'
        else: s = s + ', '.join(temp) 
        flag = flag + 1
    return s

def available_connection_classes(module):
    import inspect
    return ', '.join([name.replace('Driver_','') for name, obj in inspect.getmembers(module, inspect.isclass) if obj.__module__ is module.__name__ if name.startswith('Driver_')])
    
    
    
