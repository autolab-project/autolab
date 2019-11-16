#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

import os
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
    print('  documentation         Open the online documentation')
    print('  report                Open Github webpage to report issues and/or suggestions')
    print('  infos                 Displays the avalaible drivers and local configurations')
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
        if command=='documentation':   # Open help on read the docs
            autolab.help()
        elif command=='report':        # Open github report issue webpage
            autolab.report()
        elif command=='gui':           # GUI
            autolab.gui()
        elif command=='infos':           # GUI
            autolab.infos()
        elif command=='driver':
            driver_parser(args[2:])
        elif command=='device':
            device_parser(args[2:])
        else :
            print(f"Command {command} not known. Autolab doesn't have Super Cow Power... yet ^^")
              
            
        sys.exit()
        
        




def process_config(args_list):
    
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-D", "--driver", type=str, dest="driver", help="Set the nickname or driver to use: 1) uses nickname if it is defined in local_config.ini OR(if it is not) 2) Set the driver name to use." )
    parser.add_argument("-C", "--connection", type=str, dest="connection", help="Set the connection to use for the connection." )
    parser.add_argument("-A", "--address", type=str, dest="address", help="Set the address to use for the communication." )
    parser.add_argument("-P","--port", type=int, dest="port", help="Argument used to address different things depending on the connection type. SOCKET: the port number used to communicate, GPIB: the gpib board index, DLL: the path to the dll library." )
    parser.add_argument("-O","--other", nargs='+', dest="other", help="Set other parameters (slots,...)." )
    parser.print_help()
    args, unknown = parser.parse_known_args(args_list)
    
    config = {}
    if args.connection is not None : config['connection'] = args.connection
    if args.address is not None : config['address'] = args.address
    if args.port is not None : config['port'] = args.port
    if args.other is not None : 
        for part in args.other : 
            part = part.replace(' ','')
            config[part.split('=')[0]] = part.split('=')[1]
            
    return args.driver, config, parser
    
    
    



def driver_parser(args_list):
    # Reading of connection information
    driver, config, config_parser = process_config(args_list)
    
    # Reading of methods
    parser = argparse.ArgumentParser(add_help=False,usage='...')
    parser.add_argument("-m", "--methods", nargs='+', dest="methods", help="Set the methods to use." )
    args, unknown = parser.parse_known_args(args_list)
    
    # Instantiation
    instance = autolab.get_driver(driver,**config)
    
    # Execution of the method
    for method in args.methods :
        getattr(instance,method) 
        # ...
    
    # Driver closing
    instance.close()
    
    
    
    

def device_parser(args_list):
    
    # autolab-device -D mydummy -e amplitude -p C:\Users\               GET AND SAVE VARIABLE VALUE
    # autolab-device -D mydummy -e something                            EXECUTE ACTION
    # autolab-device -D mydummy -e amplitude -v 4                       SET VARIABLE VALUE
    # autolab-device -D mydummy -e channel1.amplitude -h                DISPLAY ELEMENT HELP

    # Reading of connection information
    driver, config, config_parser = process_config(args_list)
    
    # Parser configuration
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-e', '--element', type=str, dest="element", help='Address of the element to open' )
    parser.add_argument("-v", "--value", type=str, dest="value", help='Value to set')
    parser.add_argument("-p", "--path", type=str, dest="path", help='Path where to save data')
    parser.add_argument("-h", "--help", action='store_true', dest="help", help='Display element help')
    args, unknown = parser.parse_known_args(args_list)

    # Instantiation
    instance = autolab.get_device(driver,**config)
    element = instance
    
    # Open element
    if args.element is not None :
        for name in args.element.split('.') :
            element = getattr(element,name)
        
    # Execute order
    if args.help is True : print(element.help())
        
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
    
if __name__ == '__main__' : 
    main()
