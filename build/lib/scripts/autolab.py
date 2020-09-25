#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""


import sys
import autolab
import argparse


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
            autolab.doc()
        elif command=='report':        # Open github report issue webpage
            autolab.report()
        elif command=='gui':           # GUI
            autolab.gui()
        elif command=='infos':           # GUI
            autolab.infos()
        elif command=='stats':
            statistics(args)
        elif command=='driver':
            driver_parser(args)
        elif command=='device':
            device_parser(args)
        else :
            print(f"Command {command} not known. Autolab doesn't have Super Cow Power... yet ^^")
              
            
    sys.exit()
    
####################################################################################
################################## autolab stats ###################################      
def statistics(args_list):
    usage = f"""autolab stats [-h] [options]
    
Management of the anonymous data collection in Autolab.  \n\n
{autolab._stats.get_explanation()}
"""
    parser = argparse.ArgumentParser(add_help=False,usage=usage)
    parser.add_argument("-e", "--enable", action="store_true", dest="enable", help="Enable anonymous data collection." )
    parser.add_argument("-d", "--disable", action="store_true", dest="disable", help="Disable anonymous data collection." )
    parser.add_argument("-q", "--query", action="store_true", dest="query", help="Query anonymous data collection state." )
    parser.add_argument("-h", "--help", action="store_true", dest="help", help="Display this help message." )
    args, unknown = parser.parse_known_args(args_list)
    
    if len(args_list)==1 or args_list[1]=='-h' or args_list[1]=='--help': parser.print_help(); sys.exit()
    assert not(args.enable and args.disable), "You may either enable or disable not both"
    if args.query: print('Stats is ENABLED' if autolab.is_stats_enabled() else 'Stats is DISABLED')
    elif args.enable: autolab.set_stats_enabled(True); print('Turning stats ON permanently')
    elif args.disable: autolab.set_stats_enabled(False); print('Turning stats OFF permanently')
################################## autolab stats ###################################
####################################################################################

####################################################################################
######################### autolab driver/device utilities ##########################
def process_config(args_list):
    
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-D", "--driver", type=str, dest="driver", help="Set the nickname or driver to use: 1) uses nickname if it is defined in local_config.ini OR(if it is not) 2) Set the driver name to use." )
    parser.add_argument("-C", "--connection", type=str, dest="connection", help="Set the connection type to use for the connection." )
    parser.add_argument("-A", "--address", type=str, dest="address", help="Set the address to use for the communication." )
    parser.add_argument("-O","--other", nargs='+', dest="other", help="Set other parameters [ports (e.g SOCKET), board_index, slots,...)." )

    args, unknown = parser.parse_known_args(args_list)
    
    config = {}
    if args.connection is not None : config['connection'] = args.connection
    if args.address is not None : config['address'] = args.address
    if args.other is not None : 
        for part in args.other : 
            part = part.replace(' ','')
            config[part.split('=')[0]] = part.split('=')[1]
    
    # Help for autolab driver/device -h/--help and autolab driver/device -h/--help -D driver_name
    if not args.driver or (not args.driver and args_list[1]=='-h' or args_list[1]=='--help'): print_help_parser(parser,args_list); sys.exit()
    if args.driver and (args_list[1]=='-h' or args_list[1]=='--help'): 
        assert args.driver in autolab.list_drivers(), f"Driver {args.driver} not known"
        autolab.config_help(args.driver,_parser=True)
        sys.exit()
    
    return args.driver, config, parser

def print_help_parser(parser,args_list):
    parser.usage = f"""

----------------  General informations:  ----------------

This is a very basic help message for usage of {args_list[0]}. More info can be found on read the doc website (command: autolab doc). To display a more extensive help, please have a look at the section help below.
    
    Usage:   {args_list[0]} -D driver_name -C connection -A address -h

Recquired connection arguments (capital letters):
    -D driver_name: name of the driver to use (e.g.: agilent_33220A). driver_name can be either the driver_name or the defined nickname, as defined by the user in the local_config.ini. See below for accessing the list of available drivers.
    -C connection type to use to communicate with the device (e.g.: VISA, VXI11, SOCKET, TELNET, USB, GPIB, ...). You may access the available connections types with an help (see below helps section).
    -A address: full address to reach the device that depends on the connection type (e.g.: 192.168.0.2  [for VXI11]) and on the way you configured the instrument.
    
    
----------------  Helps (-h option)  ----------------       

Three helps are configured:
    {args_list[0]} -h
    Print this help message.
    
    {args_list[0]} -h -D driver_name
    Print useful informations on the {args_list[0].split(' ')[1]}, including available connection types, etc.
    
    {args_list[0]} -D driver_name -C connection -A address -h
    Full help message about the {args_list[0].split(' ')[1]}. This requires the address to be valid and the {args_list[0].split(' ')[1]} to be instantiated.
    
    
----------------  List of available drivers and local configurations (-D option) ----------------
   
To display the full list of available drivers and local configurations, use:
    autolab infos
    

---------------- Accepted options ----------------"""
    
    parser.print_help()
########################## autolab driver/device utilities ##########################
#####################################################################################


#####################################################################################
################################## autolab driver ###################################
def driver_parser(args_list):
    # Reading of connection information
    driver_name, config, parser = process_config(args_list)
    
    # Reading of methods
    parser.add_argument("-m", "--methods", nargs='+', dest="methods", help="Set the methods to use." )
    parser.add_argument("-h", "--help", dest="help", help="Print this help message." )
    
    # Instantiation of driver.py and driver_utilities.py
    global driver_instance
    driver_instance           = autolab.get_driver(driver_name,**config)
    
    if driver_name in autolab.list_local_configs():        
        # Load config object
        config = dict(autolab.get_local_config(driver_name))
        # Check if driver provided
        assert 'driver' in config.keys(), f"Driver name not found in driver config '{driver_name}'"
        driver_name = config['driver']
        
    driver_utilities          = autolab.load_driver_utilities_lib(driver_name+'_utilities')
    driver_utilities_instance = driver_utilities.Driver_parser(driver_instance,driver_name)
    
    # Add arguments to the existing parser (driver dependant)
    parser = driver_utilities_instance.add_parser_arguments(parser)
    
    # Add help and usage to the parser only if "-h" options requested
    if '-h' in args_list:
        dirver_infos_for_usage = build_driver_infos_for_usage(driver_name,driver_instance)
        parser.usage = driver_utilities_instance.add_parser_usage(dirver_infos_for_usage)
        parser.usage = parser.usage + f"""
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
        method_list = [method_args[0] for method_args in autolab.get_instance_methods(driver_instance)]
        for method in args.methods:
            message = None
            print(method)
            assert method.split('(')[0] in method_list, f"Method {method} not known or bound. Methods known are: {method_list}"
            print(f'\nExecuting command:  {method}')
            exec(f"message = driver_instance.{method}",globals())
            if message is not None: print(f'Return:  {message}\n')
    
    # Driver closing
    driver_utilities_instance.exit()

def build_driver_infos_for_usage(driver_name,driver_instance):
    driver_lib = autolab.load_driver_lib(driver_name)
    
    # build necessary list
    list_connection_classes = autolab.get_connection_names(driver_lib)
    list_additional_classes = autolab.get_module_names(driver_lib)
    list_instance_methods_and_args = autolab.get_instance_methods(driver_instance)
    
    mess = '\n----------------  Driver informations:  ----------------\n'
    mess += '\n    Available connections types (-C option):\n'
    for connection in list_connection_classes: 
        mess += f'     - {connection}\n'
    mess += '\n'
    mess += '\n    Available additional modules:\n'
    if list_additional_classes==[]:
        mess += f'     {list_additional_classes}'
    else:
        for additional_class in list_additional_classes: 
            mess += f'     - {additional_class}\n'
    mess += '\n'
    mess += '\n    Available methods (with arguments):'
    for method in list_instance_methods_and_args:
        mess += f'\n     - {method[0]}({",".join(method[1])})'
    mess += '\n'
            
    return mess
################################## autolab driver ###################################   
#####################################################################################


#####################################################################################
################################## autolab device ###################################
def device_parser(args_list):
    
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
    args, unknown = parser.parse_known_args(args_list)

    # Instantiation
    instance = autolab.get_device(driver_name,**config)
    element = instance
    
    # Open element
    if args.element is not None :
        for name in args.element.split('.') :
            element = getattr(element,name)
        
    # Execute order
    if args.help is True : element.help()
        
    elif args.path is not None: 
        assert element._element_type == 'variable', f"This element is not a Variable"
        value = element()
        element.save(args.path,value=value)
        
    elif args.value is not None :
        if element._element_type == 'variable' : element(args.value)
        elif element._element_type == 'action' : element(args.value)
        
    else :
        assert element._element_type in ['variable','action'], f"Please provide a Variable or Action element"
        if element._element_type == 'variable' : print(element())
        elif element._element_type == 'action' : element()
    
    instance.close()
################################## autolab device ###################################
#####################################################################################


if __name__ == '__main__' : 
    main()
