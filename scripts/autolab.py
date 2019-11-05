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
    print(f'')
    print(f'Usage:')
    print(f'  autolab <command> [options]')
    print(f'')
    print(f'Commands:')
    print(f'  driver              Shell scripting')
    print(f'  device              ')
    print(f'  gui                 Graphical User Interface')
    print(f'')

def import_module(name):
    module = __import__(name)
    globals()[module] = module
    return module

def main() :
    
    args               = sys.argv
    available_commands = ['driver','device','gui']
    
    if len(args)>1:
        assert args[1] in available_commands, f"Command {args[1]} not known. Autolab doesn't have Super Cow Power... yet ^^"
        
    # print help
    if len(args)==1 or args[1]=='-h' or args[1]=='--help':
        print_help_commands()
        sys.exit()
    
    if len(args)>2:
        assert args[2] not in available_commands, f"Please provide one command only"
        
    # modify sys.argv
    command = args[1]   # first is autolab
    sys.argv = [f'autolab_{command}.py'] + args[2:]  # first is 'autolab' and second is command
    
    # execute the appropriate module
    scripts_path = os.path.join(os.path.dirname(os.path.dirname(autolab.paths.DRIVER_SOURCES['main'])),'scripts')
    sys.path.insert(0,scripts_path)
    module = import_module(f'autolab_{command}')
    module.main()


if __name__ == '__main__' : 
    main()
