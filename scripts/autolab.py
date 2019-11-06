#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

import os
import sys
import autolab


def print_help_commands():
    print()
    print(f'Usage:')
    print(f'  autolab [-h] <command> ...')
    print()
    print(f'Commands:')
    print(f'  gui                   Open the Graphical User Interface')
    print(f'  driver                Shell scripting')
    print(f'  device                A device interface')
    print(f'  documentation         Open the online documentation')
    print(f'  report                Open github report issue online webpage')
    print()
    print(f'General Options:')
    print(f'  -h, --help            Show this help message')
    print()

def import_module(name):
    module = __import__(name)
    globals()[module] = module
    return module

def main() :
    args               = sys.argv
    available_commands = ['gui','driver','device','documentation','report']  #WARNING add manually to help too
        
    # print help
    if len(args)==1 or args[1]=='-h' or args[1]=='--help':
        print_help_commands()
        sys.exit()
    
    # Check the provided command
    if len(args)>1:
        assert args[1] in available_commands, f"Command {args[1]} not known. Autolab doesn't have Super Cow Power... yet ^^"
    if len(args)>2:
        assert args[2] not in available_commands, f"Please provide one command only"
    
    command = args[1]   # first is autolab
    if command=='documentation':   # Open help on read the docs
        autolab.help()
    elif command=='report':        # Open github report issue webpage
        autolab.report()
    elif command=='gui':           # GUI
        autolab.gui()
    else :                         # autolab_driver.py or autolab_device.py
        # modify sys.argv
        sys.argv = [f'autolab_{command}.py'] + args[2:]  # first is 'autolab' and second is command
        
        # execute the appropriate module
        scripts_path = os.path.join(os.path.dirname(os.path.dirname(autolab.paths.DRIVER_SOURCES['main'])),'scripts')
        sys.path.insert(0,scripts_path)
        module = import_module(f'autolab_{command}')
        module.main()


if __name__ == '__main__' : 
    main()
