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
    args_to_pass = init_argument_to_parse(accepted_arguments=accepted_arguments)    
    # Parser configuration can be use to write common options that won't be used by the first one
    parser = ArgumentParser(add_help=False)
    parser.add_argument("-d", "--driver", type=str, dest="driver", default=None, help="Set the nickname or driver to use: 1) uses nickname if it is defined in devices_index.ini OR(if it is not) 2) Set the driver name to use." )
    parser.add_argument("-l", "--link", type=str, dest="link", default=None, help="Set the link to use for the connection." )
    parser.add_argument("-i", "--address", type=str, dest="address", default=None, help="Set the address to use for the communication." )
    parser.add_argument("-c", "--command", nargs='+', dest="command", default=None, help="Set the commands to use." )
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
        # kwargs creation
        kwargs = dict(section)
        del kwargs['driver']
        del kwargs['connection']
        del kwargs['address']
    else:
        assert args.driver, f"Missing driver name to use"
        assert args.link and args.address, f"Missing address or connection type. Provided are, type: {args.link}, address: {args.address}"
        kwargs = {}
    
    Driver_path = [os.path.join(PATHS.DRIVERS_PATHS[key],args.driver) for key in PATHS.DRIVERS_PATHS.keys() if os.path.exists(os.path.join(PATHS.DRIVERS_PATHS[key],args.driver))]
    assert len(Driver_path) != 0, f"Warning: No driver found, full path was: {Driver_path}"
    assert len(Driver_path) == 1, f"Warning: More than one folder found with paths: {Driver_path}"
    Driver_path = Driver_path[0]
    
    sys.path.append(Driver_path)  # Add the driver's path
    
    # Import the parser module
    Driver_module = __import__(f'{args.driver}_parser')
    globals()[Driver_module] = Driver_module
    
    # Instance the driver (establish communication with the physical device)
    Instance = Driver_module.Driver_parser(args,UTILITIES,**kwargs)
    
    # Add arguments to the existing parser (driver dependant)
    parser = Instance.add_parser_arguments(parser)
    args = parser.parse_args()
    
    # Finally, execute functions according to the arguments provided
    Instance.do_something(args)
    
    
def init_argument_to_parse(accepted_arguments):
    args = sys.argv[1:]  # [1:] to remove module name
    args = ''.join(args)
    args =  ["-"+arg for arg in args.split("-") if arg]
    print(args)
    args_to_pass =  [arg   for arg in args   for acc in accepted_arguments   if acc in arg]
    print(args_to_pass)
    return args_to_pass
