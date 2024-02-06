# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

Python package for scientific experiments automation

The purpose of this package it to provide easy and efficient tools to deal with your scientific instruments, and to run automated experiments with them, by command line instructions or through a graphical user interface (GUI).

Created by Quentin Chateiller, Python drivers originally from Quentin Chateiller and Bruno Garbin, for the C2N-CNRS (Center for Nanosciences and Nanotechnologies, Palaiseau, France) ToniQ team.
Project continued by Jonathan Peltier, for the C2N-CNRS, Minaphot team.

Project hosted at https://github.com/autolab-project/autolab

Drivers made for this package can be found at https://github.com/autolab-project/autolab-drivers

Visit https://autolab.readthedocs.io/ for the full documentation of this package.
"""
import numpy  # OPTIMIZE: temporary fix to an infinite loading on some computer following the master merge (commit 25fd4d6)
import socket  # OPTIMIZE: temporary fix to an infinite loading on some computer

# Load current version in version file
from .core import paths as _paths
with open(_paths.VERSION) as version_file:
    __version__ = version_file.read().strip()
del version_file

# Process updates from previous versions
from .core import version_adapter
version_adapter.process_all_changes()
del version_adapter

# Load user config
from .core import config as _config
_config.initialize_local_directory()
_config.check_autolab_config()
_config.check_plotter_config()
_config.set_temp_folder()
_config.add_extra_driver_path()
_config.add_extra_driver_repo_url()

# infos
from .core.infos import list_devices, list_drivers, infos, config_help

# Devices
from .core.devices import get_device, close
from .core import devices as _devices

# Drivers
from .core.drivers import get_driver, explore_driver
from .core import drivers as _drivers

# Webbrowser shortcuts
from .core.web import report, doc

# Server
from .core.server import Server as server

# GUI
from .core.gui import start as gui

# Repository
from .core.repository import install_drivers
from .core import repository as _repository
_repository._check_empty_driver_folder()

del numpy
del socket

import sys
import argparse
from typing import List, Type
import autolab

def print_help():
    print()
    print('Usage:')
    print('  autolab [-h] <command> ...')
    print()
    print('Commands:')
    print('  gui                   Start the Graphical User Interface')
    print('  driver                Driver interface')
    print('  device                Device interface')
    print('  doc                   Open the online documentation (readthedocs)')
    print('  report                Open the online report/suggestions webpage (github)')
    print('  infos                 Displays the avalaible drivers and local configurations we ')
    print('  stats                 Manage the data collection state')
    print()
    print('General Options:')
    print('  -h, --help            Show this help message')
    print()


def main() :
    
    args = sys.argv
    
    # No command provided or -h/--help option : print help
    if len(args)==1 or args[1]=='-h' or args[1]=='--help':
        print_help()
        
    else :
        command = args[1]   # first is 'autolab'
        
        # Update the sys.argv for parsers
        args = [f'autolab {command}'] + args[2:]  # first is 'autolab' and second is command 
        sys.argv = args
        
        if command=='doc':   # Open help on read the docs
            doc()
        elif command=='report':        # Open github report issue webpage
            report()
        elif command=='gui':           # GUI
            gui()
        elif command=='infos':           # GUI
            infos()
        elif command=='driver':
            driver_parser(args)
        elif command=='device':
            device_parser(args)
        else :
            print(f"Command {command} not known. Autolab doesn't have Super Cow Power... yet ^^")
              
            
    sys.exit()



def process_config(args_list: List[str]):

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-D", "--driver", type=str, dest="driver", help="Set the nickname or driver to use: 1) uses nickname if it is defined in devices_config.ini OR(if it is not) 2) Set the driver name to use." )
    parser.add_argument("-C", "--connection", type=str, dest="connection", help="Set the connection type to use for the connection." )
    parser.add_argument("-A", "--address", type=str, dest="address", help="Set the address to use for the communication." )
    parser.add_argument("-O", "--other", nargs='+', dest="other", help="Set other parameters [ports (e.g SOCKET), board_index, slots,...)." )

    args, unknown = parser.parse_known_args(args_list)

    config = {}
    if args.connection is not None: config['connection'] = args.connection
    if args.address is not None: config['address'] = args.address
    if args.other is not None:
        for part in args.other:
            part = part.replace(' ', '')
            config[part.split('=')[0]] = part.split('=')[1]

    # Help for autolab driver/device -h/--help and autolab driver/device -h/--help -D driver_name
    if not args.driver or (
            (not args.driver
             and args_list[1] == '-h') or args_list[1] == '--help'):
        print_help_parser(parser,args_list); sys.exit()
    if args.driver and (args_list[1] == '-h' or args_list[1] == '--help'):
        if args.driver in autolab._devices.list_devices():
            try:
                args.driver = autolab._devices.get_final_device_config(args.driver)["driver"]
            except:
                pass
        assert args.driver in autolab._drivers.list_drivers(), f"Driver {args.driver} not known"
        autolab.config_help(args.driver,_parser=True)
        sys.exit()

    return args.driver, config, parser

def driver_parser(args_list: List[str]):

    # autolab driver -D mydummy -C CONN -A GPIB0::5::INSTR -m set_verbose(1)
    # autolab driver -D mydummy -C CONN -A GPIB0::5::INSTR -verb 1

    # Reading of connection information
    driver_name, config, parser = process_config(args_list)

    # Reading of methods
    parser.add_argument("-m", "--methods", nargs='+', dest="methods", help="Set the methods to use." )
    parser.add_argument("-h", "--help", dest="help", help="Print this help message." )

    # Instantiation of driver.py and driver_utilities.py
    global driver_instance
    assert 'connection' in config.keys(), f"Must provide a connection for the driver using -C connection with connection being for this driver among {autolab._drivers.get_connection_names(autolab._drivers.load_driver_lib(driver_name))}"
    driver_instance = autolab.get_driver(driver_name, **config)

    if driver_name in autolab._config.list_all_devices_configs():
        # Load config object
        config = dict(autolab._config.get_device_config(driver_name))
        # Check if driver provided
        assert 'driver' in config.keys(), f"Driver name not found in driver config '{driver_name}'"
        driver_name = config['driver']

    driver_utilities = autolab._drivers.load_driver_utilities_lib(driver_name + '_utilities')
    driver_utilities_instance = driver_utilities.Driver_parser(driver_instance, driver_name)

    # Add arguments to the existing parser (driver dependant)
    parser = driver_utilities_instance.add_parser_arguments(parser)

    # Add help and usage to the parser only if "-h" options requested
    if '-h' in args_list:
        dirver_infos_for_usage = build_driver_infos_for_usage(driver_name, driver_instance)
        parser.usage = driver_utilities_instance.add_parser_usage(dirver_infos_for_usage)
        parser.usage = parser.usage + """
    autolab driver -D nickname -m 'some_methods1(arg1,arg2=23)' 'some_methods2(arg1="test")'
    Execute some_methods of the driver. A list of available methods is present at the top of this help along with arguments definition. Note if strings are passed as arguments, mind the usage of ' and " (follow some_methods2 example)."""
        parser.print_help()
        sys.exit()

    args = parser.parse_args()

    # Finally, execute functions according to the arguments provided
    driver_utilities_instance.do_something(args)

    # Process given methods
    if args.methods:
        global message
        method_list = [method_args[0] for method_args in autolab._drivers.get_instance_methods(driver_instance)]
        for method in args.methods:
            message = None
            print(method)
            assert method.split('(')[0] in method_list, f"Method {method} not known or bound. Methods known are: {method_list}"
            print(f'\nExecuting command:  {method}')
            exec(f"message = driver_instance.{method}", globals())
            if message is not None: print(f'Return:  {message}\n')

    # Driver closing
    driver_utilities_instance.exit()
    
def device_parser(args_list: List[str]):

    # autolab device -D mydummy -e amplitude -p C:\Users\               GET AND SAVE VARIABLE VALUE
    # autolab device -D mydummy -e something                            EXECUTE ACTION
    # autolab device -D mydummy -e amplitude -v 4                       SET VARIABLE VALUE
    # autolab device -D mydummy -e channel1.amplitude -h                DISPLAY ELEMENT HELP

    # Reading of connection information
    driver_name, config, parser = process_config(args_list)

    # Parser configuration
    parser.add_argument('-e', '--element', type=str, dest="element", help='Address of the element to open' )
    parser.add_argument("-v", "--value", type=str, dest="value", help='Value to set')
    parser.add_argument("-p", "--path", type=str, dest="path", help='Path where to save data')
    parser.add_argument("-h", "--help", action='store_true', dest="help", help='Display element help')

    # In autolab driver, this is done after the last help request
    if "-e" in list(set([x for x in args_list if args_list.count(x) >= 2])):
        print("Warning, device will only consider the last element provided with -e. Use driver instead to do multiple operations in the same command")

    args, unknown = parser.parse_known_args(args_list)

    # Instantiation
    instance = autolab.get_device(driver_name, **config)
    element = instance

    # Open element
    if args.element is not None:
        for name in args.element.split('.'):
            element = getattr(element, name)

    # Execute order
    if args.help: element.help()

    elif args.path is not None:
        assert element._element_type == 'variable', "This element is not a Variable"
        value = element()
        element.save(args.path,value=value)

    elif args.value is not None:
        assert element._element_type in ('variable', 'action'), "Please provide a Variable or Action element using -e <element>"
        if element._element_type == 'variable': element(args.value)
        elif element._element_type == 'action': element(args.value)
    else:
        if element._element_type == 'variable': print(element())
        elif element._element_type == 'action': element()

    args = parser.parse_args()  # return error if give bad arg

    instance.close()
    
    